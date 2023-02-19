import aws_cdk as core
import aws_cdk.assertions as assertions

from hemmerbot.hemmerbot_stack import HemmerbotStack

# example tests. To run these tests, uncomment this file along with the example
# resource in hemmerbot/hemmerbot_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = HemmerbotStack(app, "hemmerbot")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
