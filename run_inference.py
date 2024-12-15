import json
import os
import tqdm
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import torch
import gc

device = "cuda" if torch.cuda.is_available() else "cpu"

# 西班牙自治区列表
COMUNIDADES = [
    "Andalucía",
    "Aragón",
    "Asturias",
    "Canary Is.",
    "Cantabria",
    "Castilla-La Mancha",
    "Castilla y León",
    "Cataluña",
    "Valenciana",
    "Extremadura",
    "Galicia",
    "Islas Baleares",
    "La Rioja",
    "Madrid",
    "Murcia",
    "País Vasco",
    "Navarra",
    "Ceuta",
    "Melilla",
]

ckpt_path = "geolocal/StreetCLIP"
ckpt_path = "results/checkpoint-1"
model = CLIPModel.from_pretrained(ckpt_path).to(device)
processor = CLIPProcessor.from_pretrained(ckpt_path)


def predict(image_paths, batch_size):
    pridicted_labels = []
    for i in tqdm.tqdm(range(0, len(image_paths), batch_size)):
        images = [
            Image.open(image_path)
            for image_path in image_paths[i : min(i + batch_size, len(image_paths))]
        ]
        inputs = processor(
            text=COMUNIDADES,
            images=images,
            return_tensors="pt",
            padding=True,
        )

        inputs = {key: value.to(device) for key, value in inputs.items()}

        outputs = model(**inputs)

        for image in images:
            image.close()

        logits_per_image = (
            outputs.logits_per_image
        )  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)
        pridicted_labels += [COMUNIDADES[i] for i in probs.argmax(dim=1).tolist()]

    return pridicted_labels


def on_pic_demo(image_path):
    with Image.open(image_path) as image:
        inputs = processor(
            text=COMUNIDADES,
            images=image,
            return_tensors="pt",
            padding=True,
        )

    inputs = {key: value.to(device) for key, value in inputs.items()}

    outputs = model(**inputs)

    logits_per_image = (
        outputs.logits_per_image
    )  # this is the image-text similarity score
    probs = logits_per_image.softmax(dim=1)

    # for each photo, Show labels ordered by decreasing probability
    return sorted(zip(COMUNIDADES, probs[0].tolist()), key=lambda x: x[1], reverse=True)


def get_accuracy(
    labels_json="dataset_spain/comunidad.json",
    images_folder="dataset_spain",
    batch_size=2,
):

    with open(labels_json, "r", encoding="utf-8") as f:
        labels = json.load(f)

    image_paths = []
    true_labels = []
    for image_id, true_comunidad in labels.items():
        image_paths.append(os.path.join(images_folder, f"{image_id}.png"))
        true_labels.append(true_comunidad)

    images = [Image.open(image_path) for image_path in image_paths]

    predicted_labels = predict(images, batch_size=batch_size)

    # 计算准确率
    print(
        f"Accuracy: {sum([1 for i, j in zip(true_labels, predicted_labels) if i == j]) / len(true_labels) * 100:.2f}%"
    )


if __name__ == "__main__":
    for label, prob in on_pic_demo("dataset_demo/20241208_143822.jpg"):
        print(f"{label}: {prob:.2%}%")
