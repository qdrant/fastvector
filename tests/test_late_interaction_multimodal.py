import os

import numpy as np

from fastembed.late_interaction_multimodal import LateInteractionMultimodalEmbedding
from tests.utils import delete_model_cache
from tests.config import TEST_MISC_DIR
from PIL import Image

# vectors are abridged and rounded for brevity
CANONICAL_IMAGE_VALUES = {
    "akshayballal/colpali-v1.2-merged": np.array(
        [
            [
                [0.015, 0.051, 0.059, 0.026, -0.061, -0.027, -0.014],
                [-0.22, -0.111, 0.046, 0.081, -0.048, -0.052, -0.086],
                [-0.184, -0.131, 0.004, 0.062, -0.038, -0.059, -0.127],
                [-0.209, -0.113, 0.015, 0.059, -0.035, -0.035, -0.072],
                [-0.031, -0.044, 0.092, -0.005, 0.006, -0.057, -0.061],
                [-0.18, -0.039, 0.031, 0.003, 0.083, -0.041, 0.088],
                [-0.091, 0.023, 0.116, -0.02, 0.039, -0.064, -0.026],
            ]
        ]
    ),
    "AndrewOgn/colpali-v1.3-merged-onnx": np.array(
        [
            [
                [-0.0345, -0.022, 0.0567, -0.0518, -0.0782, 0.1714, -0.1738],
                [-0.1181, -0.099, 0.0268, 0.0774, 0.0228, 0.0563, -0.1021],
                [-0.117, -0.0683, 0.0371, 0.0921, 0.0107, 0.0659, -0.0666],
                [-0.1393, -0.0948, 0.037, 0.0951, -0.0126, 0.0678, -0.087],
                [-0.0957, -0.081, 0.0404, 0.052, 0.0409, 0.0335, -0.064],
                [-0.0626, -0.0445, 0.056, 0.0592, -0.0229, 0.0409, -0.0301],
                [-0.1299, -0.0691, 0.1097, 0.0728, 0.0123, 0.0519, 0.0122],
            ]
        ]
    ),
}

CANONICAL_QUERY_VALUES = {
    "akshayballal/colpali-v1.2-merged": np.array(
        [
            [0.158, -0.02, 0.1, -0.023, 0.045, 0.031, 0.071],
            [-0.074, -0.111, 0.065, -0.0, -0.089, -0.003, -0.099],
            [-0.034, -0.014, 0.174, -0.063, -0.09, -0.036, 0.064],
            [-0.07, -0.014, 0.186, -0.013, -0.021, -0.062, 0.107],
            [-0.085, 0.025, 0.179, -0.101, 0.036, -0.089, 0.098],
            [-0.058, 0.031, 0.18, -0.078, 0.023, -0.119, 0.131],
            [-0.067, 0.038, 0.188, -0.079, -0.001, -0.123, 0.127],
            [-0.063, 0.037, 0.204, -0.069, 0.003, -0.118, 0.134],
            [-0.054, 0.036, 0.212, -0.072, -0.001, -0.117, 0.133],
            [-0.044, 0.03, 0.218, -0.077, -0.003, -0.107, 0.139],
            [-0.037, 0.033, 0.22, -0.088, 0.0, -0.095, 0.146],
            [-0.031, 0.041, 0.213, -0.092, 0.001, -0.088, 0.147],
            [-0.026, 0.047, 0.204, -0.089, -0.002, -0.084, 0.144],
            [-0.027, 0.051, 0.199, -0.084, -0.007, -0.083, 0.14],
            [-0.031, 0.056, 0.19, -0.082, -0.011, -0.086, 0.135],
            [-0.008, 0.108, 0.144, -0.095, -0.018, -0.086, 0.085],
        ]
    ),
    "AndrewOgn/colpali-v1.3-merged-onnx": np.array(
        [
            [-0.0023, 0.1477, 0.1594, 0.046, -0.0196, 0.0554, 0.1567],
            [-0.0139, -0.0057, 0.0932, 0.0052, -0.0678, 0.0131, 0.0537],
            [0.0054, 0.0364, 0.2078, -0.074, 0.0355, 0.061, 0.1593],
            [-0.0076, -0.0154, 0.2266, 0.0103, 0.0089, -0.024, 0.098],
            [-0.0274, 0.0098, 0.2106, -0.0634, 0.0616, -0.0021, 0.0708],
            [0.0074, 0.0025, 0.1631, -0.0802, 0.0418, -0.0219, 0.1022],
            [-0.0165, -0.0106, 0.1672, -0.0768, 0.0389, -0.0038, 0.1137],
        ]
    ),
}

queries = ["hello world", "flag embedding"]
images = [
    TEST_MISC_DIR / "image.jpeg",
    str(TEST_MISC_DIR / "small_image.jpeg"),
    Image.open((TEST_MISC_DIR / "small_image.jpeg")),
]


def test_batch_embedding():
    is_ci = os.getenv("CI")
    docs_to_embed = images

    for model_name, expected_result in CANONICAL_IMAGE_VALUES.items():
        print("evaluating", model_name)
        model = LateInteractionMultimodalEmbedding(model_name=model_name)
        result = list(model.embed_image(docs_to_embed, batch_size=2))

        for value in result:
            batch_size, token_num, abridged_dim = expected_result.shape
            assert np.allclose(value[:token_num, :abridged_dim], expected_result, atol=1e-3)
            break

        if is_ci:
            delete_model_cache(model.model._model_dir)


def test_single_embedding():
    is_ci = os.getenv("CI")
    if not is_ci:
        docs_to_embed = images

        for model_name, expected_result in CANONICAL_IMAGE_VALUES.items():
            print("evaluating", model_name)
            model = LateInteractionMultimodalEmbedding(model_name=model_name)
            result = next(iter(model.embed_images(docs_to_embed, batch_size=6)))
            batch_size, token_num, abridged_dim = expected_result.shape
            assert np.allclose(result[:token_num, :abridged_dim], expected_result, atol=2e-3)


def test_single_embedding_query():
    is_ci = os.getenv("CI")
    if not is_ci:
        queries_to_embed = queries

        for model_name, expected_result in CANONICAL_QUERY_VALUES.items():
            print("evaluating", model_name)
            model = LateInteractionMultimodalEmbedding(model_name=model_name)
            result = next(iter(model.embed_text(queries_to_embed)))
            token_num, abridged_dim = expected_result.shape
            assert np.allclose(result[:token_num, :abridged_dim], expected_result, atol=2e-3)