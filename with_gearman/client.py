import gearman
import traceback

class TweetClient(object):
    def __init__(self):
        self.gearman_client = gearman.GearmanClient( ['localhost:4730'] )

    def run(self):
        try:
            query= raw_input("Please enter Query : ")
            completed_job_request = self.gearman_client.submit_job('call_sentiment_worker', query)
            result = completed_job_request.result
            print result
            
        except Exception:
            print traceback.format_exc()

if __name__ == '__main__':
    TweetClient().run()
