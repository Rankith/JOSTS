def TrackingMiddleware(get_response):

        def middleware(request):
            """
            Save the time of last user visit
            """
            response = get_response(request)

           

            return response

        return middleware