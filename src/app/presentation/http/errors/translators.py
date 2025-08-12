from fastapi_error_map import ErrorTranslator, SimpleErrorResponseModel


class ServiceUnavailableTranslator(ErrorTranslator[SimpleErrorResponseModel]):
    @property
    def error_response_model_cls(self) -> type[SimpleErrorResponseModel]:
        return SimpleErrorResponseModel

    def from_error(self, err: Exception) -> SimpleErrorResponseModel:
        return SimpleErrorResponseModel(
            error="Service temporarily unavailable. Please try again later."
        )
