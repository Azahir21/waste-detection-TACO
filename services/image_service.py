import datetime
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
import subprocess


class ServiceImage:
    def __init__(self) -> None:
        pass

    def insert_image(self, file: UploadFile):
        try:
            content = file.file.read()
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            with open(f"assets/{filename}", "wb") as f:
                f.write(content)
        except Exception as e:
            print(e)
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()
        return filename

    def download_image(self, filename: str):
        try:
            with open(filename, "rb") as f:
                content = f.read()
        except Exception as e:
            print(e)
            return {"message": "There was an error downloading the file"}
        return FileResponse(
            f"{filename}",
            media_type="application/octet-stream",
            filename=filename,
        )

    def predict(self, file: UploadFile):
        image_path = self.insert_image(file)
        path = f"assets/{image_path}"
        command = f"yolo task=segment mode=predict model='best.pt' source={path} name='yolov8s_predict' exist_ok=True save=True save_txt=True"
        subprocess.run(command, shell=True),
        labels_filename = f"D:/kuliah/riset AAII waste management system/backend/simple-waste-detection/runs/segment/yolov8s_predict/labels/{image_path.split('.')[0]}.txt"
        object_count = self.object_count(labels_filename)
        return {
            "original_image": path,
            "result_image": f"D:/kuliah/riset AAII waste management system/backend/simple-waste-detection/runs/segment/yolov8s_predict/{image_path}",
            "object_count": object_count,
        }

    def object_count(self, filename: str):
        with open(filename, "r") as file:
            lines = file.readlines()
        first_values = [float(line.split()[0]) for line in lines]
        label_mapping = {
            0: "Aerosol",
            1: "Aluminium blister pack",
            2: "Aluminium foil",
            3: "Battery",
            4: "Broken glass",
            5: "Carded blister pack",
            6: "Cigarette",
            7: "Clear plastic bottle",
            8: "Corrugated carton",
            9: "Crisp packet",
            10: "Disposable food container",
            11: "Disposable plastic cup",
            12: "Drink can",
            13: "Drink carton",
            14: "Egg carton",
            15: "Foam cup",
            16: "Foam food container",
            17: "Food Can",
            18: "Food waste",
            19: "Garbage bag",
            20: "Glass bottle",
            21: "Glass cup",
            22: "Glass jar",
            23: "Magazine paper",
            24: "Meal carton",
            25: "Metal bottle cap",
            26: "Metal lid",
            27: "Normal paper",
            28: "Other carton",
            29: "Other plastic bottle",
            30: "Other plastic container",
            31: "Other plastic cup",
            32: "Other plastic wrapper",
            33: "Other plastic",
            34: "Paper bag",
            35: "Paper cup",
            36: "Paper straw",
            37: "Pizza box",
            38: "Plastic bottle cap",
            39: "Plastic film",
            40: "Plastic gloves",
            41: "Plastic lid",
            42: "Plastic straw",
            43: "Plastic utensils",
            44: "Polypropylene bag",
            45: "Pop tab",
            46: "Rope - strings",
            47: "Scrap metal",
            48: "Shoe",
            49: "Single-use carrier bag",
            50: "Six pack rings",
            51: "Spread tub",
            52: "Squeezable tube",
            53: "Styrofoam piece",
            54: "Tissues",
            55: "Toilet tube",
            56: "Tupperware",
            57: "Unlabeled litter",
            58: "Wrapping paper",
        }
        labels = [label_mapping[value] for value in first_values]
        count_dict = {}
        for label in labels:
            count_dict[label] = count_dict.get(label, 0) + 1
        return count_dict
