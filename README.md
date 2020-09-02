# Lambda Best Practices: EFS as Persistent Storage for functions

Mystique Unicorn App is a building new application based on microservice architectural pattern. One of their microservices need to have access to a persistent storage layer.

They have created this use-case as an analogy to explain their requirement. Let us say, we have a "Message Board", where any user can post messages and read messages of other users. This means, we need to store the messages from all the functions and generate be able to list/view of the messages. _Ofcourse, we can use a database, but that is not the point there, "How can we use a persistent storage to share data among functions?"_

Can you help them do that in Amazon API Gateway & AWS Lambda?

## 🎯Solutions

We can use AWS Elastic File System with AWS Lambda to achieve this.

![Miztiik Automation Lambda Best Practices: Persistent Storage for functions](images/miztiik_api_lambda_with_efs_architecture.png)

In this article, we will build an architecture, similar to the one shown above - A simple API using API Gateway which will trigger a Lambda function. We will have an stageVariable `lambdaAlias` and lets assume it is going to be an `prod` environment. The lambda will have multiple alias point at different stage of development. `prod` pointing to the most stable version and `dev` pointing to the bleeding edlge version.

Depending on the `lambdaAlias` value in API Gateway and Lambda `alias` pointer, the response of the API will be different. The stacks are generated using [AWS Cloud Development Kit (CDK)][102]. The architecture has been designed in a modular way so that we c``an build them individually and integrate them together. The prerequisites to build this architecture are listed below

1.  ## 🧰 Prerequisites

    This demo, instructions, scripts and cloudformation template is designed to be run in `us-east-1`. With few modifications you can try it out in other regions as well(_Not covered here_).

    - 🛠 AWS CLI Installed & Configured - [Get help here](https://youtu.be/TPyyfmQte0U)
    - 🛠 AWS CDK Installed & Configured - [Get help here](https://www.youtube.com/watch?v=MKwxpszw0Rc)
    - 🛠 Python Packages, _Change the below commands to suit your OS, the following is written for amzn linux 2_
      - Python3 - `yum install -y python3`
      - Python Pip - `yum install -y python-pip`
      - Virtualenv - `pip3 install virtualenv`

1.  ## ⚙️ Setting up the environment

    - Get the application code

      ```bash
      git clone https://github.com/miztiik/lambda-with-efs
      cd lambda-with-efs
      ```

1.  ## 🚀 Prepare the dev environment to run AWS CDK

    We will cdk to be installed to make our deployments easier. Lets go ahead and install the necessary components.

    ```bash
    # If you DONT have cdk installed
    npm install -g aws-cdk

    # Make sure you in root directory
    python3 -m venv .env
    source .env/bin/activate
    pip3 install -r requirements.txt
    ```

    The very first time you deploy an AWS CDK app into an environment _(account/region)_, you’ll need to install a `bootstrap stack`, Otherwise just go ahead and deploy using `cdk deploy`.

    ```bash
    cdk bootstrap
    cdk ls
    # Follow on screen prompts
    ```

    You should see an output of the available stacks,

    ```bash
    vpc-stack
    efs-stack
    lambda-with-efs
    ```

1.  ## 🚀 Deploying the application

    Let us walk through each of the stacks,

    - **Stack: efs-stack**
      This stack will create the Amazon EFS. There are few resources that are prerequisites to create the EFS share. This stack will create the following resources,

      - A VPC to host our EFS share - _Deployed by the dependant stack `vpc-stack`_
      - Security group for our EFS share allowing inbound `TCP` on ort `2049` from our VPC IP range
      - Posix user & acl `1000` - _In case you want to use OS level access restrictions, these will come in handy_
      - EFS Access Point to make it easier to mount to Lambda and apply resource level access restrictions
        - The default path for the access point is set to `/efs`

      Initiate the deployment with the following command,

      ```bash
      cdk deploy efs-stack
      ```

    - **Stack: lambda-with-efs**

      This stack: _lambda-with-efs_ creates an REST API with a lambda backend. This lambda function will be deployed in the same VPC as our EFS share and use the same security group(_TODO: Host lambda in a independant security group_). The stack mounts the EFS Access point to our lambda function, there-by enabling us to read and write to our EFS share.

      Initiate the deployment with the following command,

      ```bash
      cdk deploy lambda-with-efs
      ```

      Check the `Outputs` section of the stack to access the `GreetingsWallApiUrl`

1.  ## 🔬 Testing the solution

    We can use a tool like `curl` or `Postman` to query the url. The _Outputs_ section of the respective stacks has the required information on the urls.

    ```bash
    $ GREETINGS_WALL_URL="https://2s9p0x3p53.execute-api.us-east-2.amazonaws.com/prod/lambda-with-efs/greeter"
    $ curl ${GREETINGS_WALL_URL}
    No message yet.
    $ curl -X POST -H "Content-Type: text/plain" -d 'Hello from EFS!' ${GREETINGS_WALL_URL}
    Hello from EFS!

    $ curl -X POST -H "Content-Type: text/plain" -d 'Hello again :)' ${GREETINGS_WALL_URL}
    Hello from EFS!
    Hello again :)

    $ curl ${GREETINGS_WALL_URL}
    Hello from EFS!
    Hello again :)

    $ curl -X DELETE ${GREETINGS_WALL_URL}
    Messages deleted.

    $ curl ${GREETINGS_WALL_URL}
    No message yet.
    ```

    You should be able observe that we were able to read, write & delete data from the EFS share.

1.  ## 📒 Conclusion

    Here we have demonstrated how to use EFS along with AWS Lambda to create a persistent storage for your functions. This can be really helpful in a variety of situations. For example,

    - If you are running machine language inference, lambda internal storage and layers might not be enough to host all the dependant libraries. In those cases an external storage becomes a necessity.
    - Another usecase is when you want to process really huge files - unpack/zip them. Then the extra scratch space offered EFS comes handy.

    If you know of other usecases for using EFS with lambda, do let me know.

1)  ## 🧹 CleanUp

    If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

    - Resources created during [Deploying The Application](#deploying-the-application)
    - Delete CloudWatch Lambda LogGroups
    - _Any other custom resources, you have created for this demo_

    ```bash
    # Delete from cdk
    cdk destroy

    # Follow any on-screen prompts

    # Delete the CF Stack, If you used cloudformation to deploy the stack.
    aws cloudformation delete-stack \
        --stack-name "MiztiikAutomationStack" \
        --region "${AWS_REGION}"
    ```

    This is not an exhaustive list, please carry out other necessary steps as maybe applicable to your needs.

## 📌 Who is using this

This repository aims to teach best practices & advanced file system techniques to new developers, Solution Architects & Ops Engineers in AWS. Based on that knowledge these Udemy [course #1][103], [course #2][102] helps you build complete architecture in AWS.

### 💡 Help/Suggestions or 🐛 Bugs

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional documentation or solutions, we greatly value feedback and contributions from our community. [Start here][200]

### 👋 Buy me a coffee

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q41QDGK) Buy me a [coffee ☕][900].

### 📚 References

1. [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate – Part 1][1]

1. [AWS Blog][5] & [Use Lambda & EFS to process big files][2]

1. [Use Lambda & EFS to Update Fargate Web Content][2]

1. [Use Lambda & EFS I/O Performance][3]

1. [Lambda & EFS to run ML Inference][4]

### 🏷️ Metadata

**Level**: 300

![miztiik-success-green](https://img.shields.io/badge/miztiik-success-green)

[1]: https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/
[2]: https://github.com/aws-samples/aws-lambda-efs-samples
[3]: https://lumigo.io/blog/unlocking-more-serverless-use-cases-with-efs-and-lambda/
[4]: https://aws.amazon.com/blogs/aws/new-a-shared-file-system-for-your-lambda-functions/
[5]: https://aws.amazon.com/blogs/compute/using-amazon-efs-for-aws-lambda-in-your-serverless-applications/
[100]: https://www.udemy.com/course/aws-cloud-security/?referralCode=B7F1B6C78B45ADAF77A9
[101]: https://www.udemy.com/course/aws-cloud-security-proactive-way/?referralCode=71DC542AD4481309A441
[102]: https://www.udemy.com/course/aws-cloud-development-kit-from-beginner-to-professional/?referralCode=E15D7FB64E417C547579
[103]: https://www.udemy.com/course/aws-cloudformation-basics?referralCode=93AD3B1530BC871093D6
[200]: https://github.com/miztiik/lambda-with-efs/issues
[899]: https://www.udemy.com/user/n-kumar/
[900]: https://ko-fi.com/miztiik
[901]: https://ko-fi.com/Q5Q41QDGK
