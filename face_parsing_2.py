{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "private_outputs": true,
      "provenance": [],
      "authorship_tag": "ABX9TyNHbiMtUBzGrmAmCGWpxpbm",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/fluanceifi/NoTeamNurd/blob/develop/face_parsing_2.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "collapsed": true,
        "id": "z2iozabgYrYe"
      },
      "outputs": [],
      "source": [
        "import matplotlib.pyplot as plt\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import cv2\n"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "pip install git+https://github.com/FacePerceiver/facer.git@main"
      ],
      "metadata": {
        "collapsed": true,
        "id": "NHGF0L_Kc3FI"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": [],
      "metadata": {
        "id": "Ew15ENLUb-LB"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from google.colab import files\n",
        "\n",
        "# 파일 업로드\n",
        "uploaded = files.upload()\n"
      ],
      "metadata": {
        "id": "4eviXdlhfbKK"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "import torch\n",
        "import facer\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "\n",
        "# 1. 이미지 로드 및 face parsing\n",
        "device = 'cuda' if torch.cuda.is_available() else 'cpu'\n",
        "image = facer.hwc2bchw(facer.read_hwc('/content/woojin.png')).to(device)\n",
        "\n",
        "face_detector = facer.face_detector('retinaface/mobilenet', device=device)\n",
        "with torch.inference_mode():\n",
        "    faces = face_detector(image)\n",
        "\n",
        "face_parser = facer.face_parser('farl/lapa/448', device=device)\n",
        "with torch.inference_mode():\n",
        "    faces = face_parser(image, faces)"
      ],
      "metadata": {
        "id": "sTKc4ry2V44w"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# 2. 세그멘테이션 결과\n",
        "seg_logits = faces['seg']['logits']\n",
        "seg_probs = seg_logits.softmax(dim=1)\n",
        "parsed_classes = seg_probs.argmax(dim=1)"
      ],
      "metadata": {
        "id": "amJnCcb1V_JR"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# 3. 추출하고 싶은 부위 리스트 (좌우 통합 포함)\n",
        "merged_labels = {\n",
        "    'face_skin': [1],\n",
        "    'eyebrows': [2, 3],\n",
        "    'eyes': [4, 5],\n",
        "    'nose': [6],\n",
        "    'lips': [7, 9],\n",
        "    'inner_mouth': [8],\n",
        "    'hair': [10]\n",
        "}"
      ],
      "metadata": {
        "id": "9FoQ2KS3WBI6"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# 4. 부위별 추출\n",
        "extracted_parts = {}\n",
        "\n",
        "for part_name, class_indices in merged_labels.items():\n",
        "    mask = torch.zeros_like(parsed_classes, dtype=torch.bool)\n",
        "    for idx in class_indices:\n",
        "        mask |= (parsed_classes == idx)\n",
        "    part_image = image * mask.unsqueeze(1).float()  # [B, C, H, W]\n",
        "    extracted_parts[part_name] = part_image"
      ],
      "metadata": {
        "id": "s9bGjnT3WEQZ"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "plt.figure(figsize=(16, 10))\n",
        "for i, (part_name, part_img) in enumerate(extracted_parts.items()):\n",
        "    plt.subplot(2, 4, i + 1)\n",
        "    facer.show_bchw(part_img)\n",
        "    plt.title(part_name)\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "## 여기까지 부위 추출 관련 코드 - 그 다음부터는 색 추출"
      ],
      "metadata": {
        "collapsed": true,
        "id": "ua34jY6jWF8x"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "print(image.shape)"
      ],
      "metadata": {
        "id": "N1XyRZcXfHYU"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# 원본이미지 [1, 3, H, W] → NumPy [H, W, 3] - 원본이미지를 NumPy에서 쓰기 위해서 변환하는과정.\n",
        "image_np = image[0].permute(1, 2, 0).cpu().numpy()  # shape: (506, 524, 3)\n",
        "\n",
        "plt.imshow(image_np)"
      ],
      "metadata": {
        "collapsed": true,
        "id": "FBAWW02RxFkx"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "import numpy as np\n",
        "import cv2\n",
        "\n",
        "# 1. 피부 부위 마스크 생성 (클래스 번호 1 = face_skin) - True / False 로 구분된 이미지 - 피부부위 마스크를 만들기 위해서\n",
        "skin_mask_tensor = (parsed_classes == 1)\n",
        "skin_mask = skin_mask_tensor.squeeze().cpu().numpy().astype(bool)  # shape: (H, W)\n",
        "plt.imshow(skin_mask)"
      ],
      "metadata": {
        "id": "SWp5rIU-50Iq",
        "collapsed": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "skin_pixels = image_np[skin_mask]\n",
        "\n",
        "\n",
        "# 마스크에서 피부라고 인식한 이미지에 해당하는 픽셀의 값의 평균을 구한다.\n",
        "if skin_pixels.shape[0] == 0:\n",
        "    print(\"❗️마스크에 해당하는 픽셀이 없습니다.\")\n",
        "else:\n",
        "    mean_rgb = np.mean(skin_pixels, axis=0)\n",
        "    print(f\"📊 평균 RGB 값: R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f}, B={mean_rgb[2]:.1f}\")\n",
        "\n"
      ],
      "metadata": {
        "id": "cMcJdn2hx-vt"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}