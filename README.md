
## Prerequisites

Running this stack requires the installation of the following components:

* **AutoGen**: [Installation instructions](https://github.com/link-to-autogen-installation)
* **LiteLLM**
* **Ollama**

> **Note**: We recommend using a virtual environment for your stack. [See this article](https://realpython.com/python-virtual-environments-a-primer/) for guidance on setting up a virtual environment.

## Installation Instructions

### 1. Installing LiteLLM
 
To install LiteLLM with proxy server functionality, use the following command:

```
pip install 'litellm[proxy]
```

Note: If you're using Windows, it's recommended to run LiteLLM and Ollama within a WSL2 environment.

### 2. Installing Ollama

Mac and Windows: Download Ollama from the official website.
Linux: Run the following command in your terminal:

```
curl -fsSL https://ollama.com/install.sh | sh
```
### 3.Downloading Models

Ollama provides a library of models that you can use. Before you can use a model, you need to download it. For example, to download the llama3:instruct model, run:

```
ollama pull llama3:instruct
```

To view the models you have downloaded and are available for use, run:

```
ollama list
```

## Running the LiteLLM Proxy Server
To run LiteLLM with a model you have downloaded, use the following command in your terminal:

```
litellm --model ollama/llama3:instruct
```


