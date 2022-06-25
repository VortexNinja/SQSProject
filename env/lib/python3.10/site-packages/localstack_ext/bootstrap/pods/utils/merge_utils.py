import logging
from typing import Callable,Optional
from moto.s3.models import FakeBucket
from moto.sqs.models import Queue
from localstack_ext.bootstrap.state_merge_ddb import merge_dynamodb
from localstack_ext.bootstrap.state_merge_kinesis import merge_kinesis
LOG=logging.getLogger(__name__)
def get_merge_function_for_assets(service):
	match service:
		case'dynamodb':return merge_dynamodb
		case'kinesis':return merge_kinesis
		case _:return None
def is_special_case(obj):return isinstance(obj,(Queue,FakeBucket))