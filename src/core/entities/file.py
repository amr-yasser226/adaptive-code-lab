class File : 
    def __init__(self , id , submission_id , uploader_id , path , file_name, content_type , size_bytes , check_sum , storage_url , created_at ):
        self.__id = id
        self.__submission_id = submission_id
        self.uploader_id = uploader_id
        self.path = path
        self.file_name = file_name
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.checksum = check_sum
        self.storage_url = storage_url
        self.created_at = created_at
    def get_id(self):
            return self.__id
    def get_submission_id(self):
            return self.__submission_id
    # def save_file(self):
    #     pass
    # def delete_file(self):
    #     pass
    # def get_stream(self):
    #     pass
    # def generate_singned_url(self , expiration_time):
    #     pass
    # def validate(self):
    #     pass