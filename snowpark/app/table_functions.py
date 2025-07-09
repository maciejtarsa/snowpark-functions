from common import print_hello


class TransformTable:
    def __init__(self):
        # define any parameters or initial setup here
        self._id = ""
        self._new_value = ""

    def process(self, id, value):
        # processes each input row
        self._id = id
        self._new_value = print_hello(value)
        yield (self._id, self._new_value)

    # def end_partition(self):
    #     # Optional if these are to be used in partitioning
    #     # finalises processing of input partitions
    #     yield (self._id, self._new_value)

# For local debugging (optional)
if __name__ == "__main__":
    # Sample data simulating a partition
    sample_rows = [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie"),
    ]
    print("Results from end_partition():")
    for row in sample_rows:
        tf = TransformTable()
        tf.process(*row)
        for result in tf.end_partition():
            print(result)
