import os
from pymongo import MongoClient
from loguru import logger

class MongoDB:

    def __init__(self) -> None:
        client = MongoClient(os.getenv('MONGODB_URI', ''))
        db = client['bot']
        self.collection = db["clients"]
        pass


    def client_exist(self, client_id):
        result = self.collection.find_one({"w_id": client_id})
        return result


    def set_steps_to_client_temporal(self, client_id, steps):
        logger.info(client_id)
        result = self.collection.update_one(
            {"w_id": client_id},
            {"$set": {"steps_temporal": steps}}
        )

        if result.modified_count > 0:
            logger.info("steps assigned.")
        else:
            logger.error("steps not assigned.")


    def set_steps_to_client(self, client_id):
        logger.info(f"Setting steps for client: {client_id}")
        client = self.client_exist(client_id=client_id)
        
        if "steps_temporal" in client:
            result = self.collection.update_one(
                {"w_id": client_id},
                {
                    "$set": {"steps": client["steps_temporal"]},
                    "$unset": {"steps_temporal": ""}
                }
            )
            if result.modified_count > 0:
                logger.info("Steps assigned from steps_temporal.")
            else:
                logger.error("Failed to assign steps from steps_temporal.")
        else:
            if "steps" in client:
                logger.info("Client already has steps assigned.")
            else:
                logger.error("Client has neither steps_temporal nor steps assigned.")


    def mark_step_as_complete(self, client_id, unique_function_name):
        result = self.collection.update_one(
            {"w_id": client_id, "steps.function": unique_function_name},
            {"$set": {"steps.$.complete": True}}
        )

        if result.modified_count > 0:
            logger.info("added complete to step.")
        else:
            logger.error("error on add complete to step.")


    def add_image_to_step(self, client_id, unique_function_name, image_url):
        result = self.collection.update_one(
            {"w_id": client_id, "steps.function": unique_function_name},
            {"$push": {"steps.$.images": image_url}}
        )

        if result.modified_count > 0:
            logger.info("images added.")
        else:
            logger.error("error on add images.")
    

    def reset_images_to_step(self, client_id, unique_function_name):
        result = self.collection.update_one(
            {"w_id": client_id, "steps.function": unique_function_name},
            {"$set": {"steps.$.images": []}}
        )

        if result.modified_count > 0:
            logger.info("images reset.")
        else:
            logger.error("error on reset images.")


    def remove_item(self, client_id):
        result = self.collection.delete_one({"w_id": client_id})
        if result.deleted_count > 0:
            logger.info("Registro eliminado con éxito.")
        else:
            logger.error("No se encontró el registro para eliminar.")


    def get_step_by_client(self, client_id: str):
        pipeline = [
            {"$match": {"w_id": client_id}},
            {"$unwind": "$steps"},
            {"$match": {"steps.complete": False}},
            {"$limit": 1},
            {"$replaceRoot": {"newRoot": "$steps"}}
        ]
        
        result = self.collection.aggregate(pipeline)
        for step in result:
            return step

        return None

    
    def create_client(self, client_id, report):
        insert = {
            "w_id": client_id,
            "steps": [
                
            ],
            "report": report
        }
        result = self.collection.insert_one(insert)

        if result.acknowledged:
            return self.client_exist(client_id=client_id)
        else:
            return None
        
