from ultralytics import YOLO
import cv2
import numpy as np
import urllib.request
import uvicorn
import random

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, User, Result

app = FastAPI()

class ClassifyInput(BaseModel):
    url: str
    plant_id: int
    user_id: int

class UserFind(BaseModel):
    user_id: int    

class UserIO(BaseModel):
    id: int
    name: str

# create and manage session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# load model    
model_detect = YOLO('trained/detect/best.pt')
model_cls = YOLO('trained/cls/best.pt')

# input image
def input_image(url):
    try:
        # Download the image from the URL
        with urllib.request.urlopen(url) as url:
            image_array = np.asarray(bytearray(url.read()), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Check if the image was successfully loaded
        if image is None:
            print("Error: Unable to load image.")
        else:
            org_h, org_w, *_ = image.shape
            return image, org_h, org_w
    except Exception as e:
        print(f"Error: {e}")

# check xa gần
def checknearfar(image, org_h, org_w):
    org_area = org_h * org_w
    results = model_detect(image)

    if results is None:
        print("Error: results is None.")
        return
    
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        result.show()
        # print(boxes.conf)  # print results
        largest = max(boxes.conf)
        for box in boxes:
            if box.conf == largest:
                left, top, right, bottom = np.array(box.xyxy.cpu(), dtype=np.int64).squeeze()
                width = right - left
                height = bottom - top
                area = width * height
                break
        
    return org_area / area

# check mờ
def estimate_blur(image, threshold: int = 150):
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_map = cv2.Laplacian(image, cv2.CV_64F)
    score = np.var(blur_map)
    return bool(score < threshold)

# model cls
def cls_pests(image):
    return model_cls.predict(source=image)

@app.post("/register")
async def register(user: UserIO, db: Session = Depends(get_db)):
    new_user = User(
        id = user.id,
        name = user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

@app.post("/predict")
async def main(input: ClassifyInput, db: Session = Depends(get_db)):
    print(model_cls)
    print(model_detect)
    if input.plant_id != 0:
        return "Not tomato"
    # url image: https://laidbackgardener.blog/wp-content/uploads/2017/08/20170815a-max-pixel.jpg
    # url non-image: https://console.cloud.google.com
    image_url = input.url
    # image_url = input("Enter the URL of the image: ")
    # while input_image(image_url) is None:
    #     image_url = input("Enter the URL of the image: ")
    #     image = input_image(image_url)
    
    # print("Image successfully loaded.")
    image, org_h, org_w = input_image(image_url)
    ratio = checknearfar(image, org_h, org_w)
    if ratio <= 10:
        blur = estimate_blur(image)
        if blur:
            return "Image is not fine!"
        else:
            cls_result = cls_pests(image)
            percent = float(cls_result[0].probs.top1conf.cpu().numpy())
            pests_index = cls_result[0].probs.top1
            pests_name = cls_result[0].names[pests_index]
            print("{:.2f}%".format(percent*100))
            print(pests_name)
            
            # Create new result and add it into database
            new_result = Result(
                id = random.shuffle(list(range(1, 99999))),
                plant_id=input.plant_id,
                url=image_url,
                pest=pests_name,
                percentage=percent,
                user_id=input.user_id
            )
            db.add(new_result)
            db.commit()
            db.refresh(new_result)

            return {"url": image_url, "Pest": pests_name, "Percentage": percent}
    else:
        print("!OK")

@app.post("/historyUser")
async def historyUser(user: UserFind, db: Session = Depends(get_db)):
    user_id = user.user_id 
    result = db.query(
        Result
    ).join(User).filter(User.id == user_id).all()
    return result

# Run the main function
if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)