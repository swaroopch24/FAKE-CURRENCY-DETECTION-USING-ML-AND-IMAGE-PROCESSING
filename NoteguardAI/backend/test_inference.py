import os
import asyncio
from pathlib import Path

def test_inference():
    import sys
    sys.path.append(str(Path(__file__).parent.resolve()))
    from src.modules.ai_engine.pipeline import AIInferencePipeline
    
    img_path = Path("../dataset/split/val/real_2000/14.jpg")
    print(f"Testing image: {img_path}")
    if not img_path.exists():
        print("Image does not exist!")
        return

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    pipeline = AIInferencePipeline()
    result = pipeline.process_inference(img_bytes)
    print("Pipeline Result:")
    print(result)

if __name__ == "__main__":
    test_inference()
