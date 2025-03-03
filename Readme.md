# Automated tests
Inference libraries are selected via env. variables. To optimize CPU inference time we use ollama and stable-diffusion.cpp by default \
Since ollama does not support qwen2.5-vl yet, some image functionality is diabled in this scenario, \
and evaluation module performs worse \
For full-featured automated test on GPU set env to use both tarnsformers and diffuesers
```
export USE_TRANSFORMERS=1
export USE_DIFFUSERS=1
```
# Running steps

## Common steps

1) Run OpenUI
```
# Windows and Mac
docker run --add-host=host.docker.internal:host-gateway --rm --name openui -p 7878:7878 -e OLLAMA_HOST=http://host.docker.internal:11434 ghcr.io/wandb/openui
# Linux
docker run --add-host=host.docker.internal:172.17.0.1 --rm --name openui -p 7878:7878 -e OLLAMA_HOST=http://host.docker.internal:11434 ghcr.io/wandb/openui
```

2) Install & run ollama:
```
curl -fsSL https://ollama.com/install.sh | sh
export OLLAMA_HOST=0.0.0.0:11434               # on Linux set ollama to listen to container
ollama serve | tee ollama_log.txt              # this log is very important for openui baseline
ollama pull qwen2.5
```

## Instructions for better CPU inference

0) Pull submodules
```
git submodule init
git submodule update
```

1) Compile stable-diffusion.cpp && add binary to path:
```
cd stable-diffusion.cpp
git pull origin master
git submodule init
git submodule update
mkdir build
cd build
cmake ..
cmake --build . --config Release

export PATH=$HOME/llm-for-gui/stable-diffusion.cpp/build/bin:$PATH
```

2) Pull both diffusion models:
```
mkdir models
cd models
curl -L -O https://huggingface.co/Jl-wei/ui-diffuser-v2/resolve/main/pytorch_lora_weights.safetensors
curl -L -O https://huggingface.co/stabilityai/stable-diffusion-2-base/resolve/main/512-base-ema.safetensors
```

3) Install requirements:
```
pip install -r requirements_cpu.txt
```

4) Install firefox for playwright:
```
playwright install firefox
```
5) For llm-evaluation pull vision model
```
ollama pull llava
```

## Instructions for full-featured GPU inference
0) Set env to use transormers and diffusers
```
export USE_TRANSFORMERS=1
export USE_DIFFUSERS=1
```
1) Install requirements:
```
@TODO:
```
# LLM
