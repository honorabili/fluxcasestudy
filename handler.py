import runpod
import json
from huggingface_hub import login
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import base64
import torch
from transformers import AutoModel
import os
from transformers import PreTrainedModel, PretrainedConfig
# You might need a custom config and model class here

hf_token = os.getenv('HF_TOKEN')  # This fetches the token from the environment variable


model_id = "black-forest-labs/FLUX.1-dev"
MODEL_PATH = "/app/model"
model_name = "black-forest-labs/FLUX.1-dev"
# Token will need to be updated if it refreshes
model = AutoModel.from_pretrained(model_name, token=hf_token)


# Load the pre-downloaded model
scheduler = EulerDiscreteScheduler.from_pretrained(MODEL_PATH, subfolder="scheduler")
pipeline = StableDiffusionPipeline.from_pretrained(MODEL_PATH, scheduler=scheduler, torch_dtype=torch.float16)
pipeline = pipeline.to("cuda")

print("Model is ready for use")

def handler(event, context=None):
    # Parse input
    try:
        body = event.get("input", {})
        prompt = body.get("prompt", "A futuristic cityscape at sunset")
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Invalid JSON input."}

    if not prompt:
        return {"statusCode": 400, "body": "Prompt is required."}

    # Generate image
    try:
        print(f"Generating image for prompt: {prompt}")
        images = pipeline(prompt, num_inference_steps=50, guidance_scale=7.5).images
        image_data = []

        print("No. of images genereated = ", len(images))
        for idx, img in enumerate(images):
            # Convert image to a format suitable for response
            img_path = f"/tmp/image_{idx}.png"
            print(f"Saving image - {img_path}")
            img.save(img_path)
            with open(img_path, "rb") as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                image_data.append(image_base64)
            break

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": image_data[0]
        }

    except Exception as e:
        print(f"Error generating image: {e}")
        return {"statusCode": 500, "body": str(e)}

# Debugging locally
if __name__ == "__main__":
    runpod.serverless.start({'handler': handler})
