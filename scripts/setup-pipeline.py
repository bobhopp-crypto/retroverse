cat << 'EOF' > run_generation.py
import json, time, requests, sys

BASE_URL = "http://127.0.0.1:8188"

workflow = {
    "1": {
        "inputs": {"ckpt_name": "sd15.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "2": {
        "inputs": {"text": "", "clip": ["1", 1]},
        "class_type": "CLIPTextEncode"
    },
    "3": {
        "inputs": {"text": "", "clip": ["1", 1]},
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {"width": 512, "height": 512, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    },
    "5": {
        "inputs": {
            "seed": 1,
            "steps": 20,
            "cfg": 7,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": ["1", 0],
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["4", 0]
        },
        "class_type": "KSampler"
    },
    "6": {
        "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    },
    "7": {
        "inputs": {"filename_prefix": "batch", "images": ["6", 0]},
        "class_type": "SaveImage"
    }
}

def generate(prompt):
    wf = json.loads(json.dumps(workflow))
    wf["2"]["inputs"]["text"] = prompt
    wf["3"]["inputs"]["text"] = ""

    r = requests.post(f"{BASE_URL}/prompt", json={"prompt": wf})
    data = r.json()

    if "prompt_id" not in data:
        print("ERROR:", data)
        return None

    pid = data["prompt_id"]

    while True:
        time.sleep(1)
        h = requests.get(f"{BASE_URL}/history/{pid}").json()
        if pid in h:
            outputs = h[pid]["outputs"]
            for node in outputs.values():
                if "images" in node:
                    return node["images"][0]["filename"]

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:])
    if not prompt:
        print("No prompt provided")
        sys.exit(1)

    result = generate(prompt)
    print("OUTPUT:", result)
EOF