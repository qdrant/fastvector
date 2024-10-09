from typing import Sequence, Optional, List, Dict, Iterable
from pathlib import Path

import numpy as np
from tokenizers import Encoding

from fastembed.common.onnx_model import OnnxModel, OnnxProvider
from fastembed.common.preprocessor_utils import load_tokenizer
from fastembed.common.utils import iter_batch


class OnnxCrossEncoderModel(OnnxModel):
    ONNX_OUTPUT_NAMES: Optional[List[str]] = None

    def load_onnx_model(
        self,
        model_dir: Path,
        model_file: str,
        threads: Optional[int],
        providers: Optional[Sequence[OnnxProvider]] = None,
    ) -> None:
        super().load_onnx_model(
            model_dir=model_dir,
            model_file=model_file,
            threads=threads,
            providers=providers,
        )
        self.tokenizer, _ = load_tokenizer(model_dir=model_dir)

    def tokenize(self, query: str, documents: List[str], **kwargs) -> List[Encoding]:
        return self.tokenizer.encode_batch([(query, doc) for doc in documents])

    def onnx_embed(self, query: str, documents: List[str], **kwargs) -> List[float]:
        tokenized_input = self.tokenize(query, documents, **kwargs)

        inputs = {
            "input_ids": np.array([enc.ids for enc in tokenized_input]),
            "attention_mask": np.array([enc.attention_mask for enc in tokenized_input]),
        }
        input_names = {node.name for node in self.model.get_inputs()}
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = np.array([enc.type_ids for enc in tokenized_input])

        onnx_input = self._preprocess_onnx_input(inputs, **kwargs)
        outputs = self.model.run(self.ONNX_OUTPUT_NAMES, onnx_input)
        return outputs[0][:, 0].tolist()

    def _rerank_documents(
        self, query: str, documents: Iterable[str], batch_size: int, **kwargs
    ) -> Iterable[float]:
        for batch in iter_batch(documents, batch_size):
            yield from self.onnx_embed(query, batch, **kwargs)

    def _preprocess_onnx_input(
        self, onnx_input: Dict[str, np.ndarray], **kwargs
    ) -> Dict[str, np.ndarray]:
        """
        Preprocess the onnx input.
        """
        return onnx_input
