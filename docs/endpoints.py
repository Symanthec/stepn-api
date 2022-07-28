# This tutorial exploits login function from previous tutorial
# and assumes you've read it
from basics import login

if __name__ == '__main__':
    # This will not log in, but you can try with your STEPN account.
    client = login("mail@example.org", "123456")

    if client:
        # While not endpoints are implemented with methods
        # You can make calls to the server by calling
        body = client.run("userbasic")

        """
        This will be converted to
        https://api.stepn.com/run/userbasic
        """

        # All successful responses will be in JSON format
        # Client.run() function will return parsed response as "dict"
        # In case of failure, an exception will be thrown
        if body['code'] == 0:
            """ Response code 0 means success """
            print("Server response:", body)

        """
        Requests have 3 outcomes:
            1. Non-existing endpoint:
                "had error deal:/run/bad-endpoint-here
            2. Existing endpoint, but some error occurred, like the following:
                { "code":102001, "msg":"Player hasnt logged in yet" }
            3. Existing endpoint, success:
                { "code": 0, "data": [] }
        """

        # If you need to add parameters, put them in a dictionary
        parameters = {
            "orderId": 123456789
        }
        body = client.run("orderdata", parameters)
        print("Order data:", body)

        """
        By default client sends GET requests. 
        
        If you'll ever need to use another method,
        use functions from "requests" library 
        """
        try:
            import requests

            client.run("someEndpoint", method=requests.post)
        except RuntimeError:
            print("'someEndpoint' endpoint does not exist!")
