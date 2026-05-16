def evaluate_response(response: str):

    return {
        "characters": len(response),
        "words": len(response.split()),
        "is_empty": len(response.strip()) == 0
    }


class Evaluator:
    
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0

    def log_success(self):
        self.total += 1
        self.success += 1

    def log_failure(self):
        self.total += 1
        self.failed += 1

    def report(self):
        if self.total == 0:
            return "No requests yet"

        return {
            "Total": self.total,
            "Success": self.success,
            "Failed": self.failed
        }