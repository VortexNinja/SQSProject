from localstack.runtime import hooks
from localstack_ext.plugins import api_key_configured
@hooks.on_infra_start(should_load=lambda:api_key_configured())
def add_iam_enforcement_listener():from localstack.aws.handlers import serve_custom_service_request_handlers as A;from localstack_ext.services.iam.legacy_handler import LegacyIamEnforcementHandler as B;A.handlers.append(B())