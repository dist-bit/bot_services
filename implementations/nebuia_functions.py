import os
import re
from aiohttp_retry import Any
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool

from typing import Callable, Dict, List
from database.mongo import MongoDB
from implementations.abstract_functions_client import AbstractClientFunctions
from loguru import logger

import http.client
import io
import json

from models.report import ReportID
from models.address import AddressParser
from models.spoof_face import FaceSpoofing
from models.quality_face import FaceQuality
from models.id import IDResult
from store.redis import Redis


class NebuIAAPI():

    def __init__(self) -> None:
        self.headers = {
            'api_key': os.getenv('NEBUIA_API_KEY', ''),
            'api_secret': os.getenv('NEBUIA_API_SECRET', ''),
            'Content-Type': 'application/json'
        }

        self.conn = http.client.HTTPSConnection("api.nebuia.com")
        pass

    def get_report(self, report):
        self.conn.request(
            "GET", f"/api/v1/services/report?report={report}", headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))
        return ReportID.from_dict(data)

    def save_email(self, email, report) -> bool:
        payload = json.dumps({
            "email": email
        })
        self.conn.request(
            "PUT", f"/api/v1/services/email?report={report}", payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))
        return data["status"]

    def send_otp(self, report) -> bool:
        self.conn.request(
            "GET", f"/api/v1/services/otp/generate/email?report={report}", "", self.headers)
        res = self.conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))
        return data["status"]

    def verify_otp(self, report, code) -> bool:
        self.conn.request(
            "GET", f"/api/v1/services/otp/validate/email/{code}?report={report}", "", self.headers)
        res = self.conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))
        return data["status"]

    def check_face_quality(self, report, image_bytes1) -> FaceQuality:
        url = f"/api/v1/services/face/quality?report={report}"
        image_in_memory1 = io.BytesIO(image_bytes1)
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="face"; filename="image.jpg"\r\n'
            f'Content-Type: image/jpeg\r\n\r\n'
        ).encode('utf-8') + image_in_memory1.getvalue() + (
            f'\r\n--{boundary}--\r\n'
        ).encode('utf-8')

        self.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        self.headers['Content-Length'] = str(len(body))

        self.conn.request("POST", url, headers=self.headers, body=body)
        res = self.conn.getresponse()
        data = res.read()

        data = json.loads(data.decode("utf-8"))
        return FaceQuality.from_dict(data)

    def check_face_spoofing(self, report, image_bytes1) -> FaceQuality:
        url = f"/api/v1/services/face?report={report}"
        image_in_memory1 = io.BytesIO(image_bytes1)
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="face"; filename="image.jpg"\r\n'
            f'Content-Type: image/jpeg\r\n\r\n'
        ).encode('utf-8') + image_in_memory1.getvalue() + (
            f'\r\n--{boundary}--\r\n'
        ).encode('utf-8')

        self.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        self.headers['Content-Length'] = str(len(body))

        self.conn.request("POST", url, headers=self.headers, body=body)
        res = self.conn.getresponse()
        data = res.read()

        data = json.loads(data.decode("utf-8"))
        return FaceSpoofing.from_dict(data)

    def check_address_document(self, report, pdf_bytes1) -> FaceQuality:
        url = f"/api/v1/services/address?report={report}"
        pdf_memory = io.BytesIO(pdf_bytes1)
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="document"; filename="doc.pdf"\r\n'
            f'Content-Type: application/pdf\r\n\r\n'
        ).encode('utf-8') + pdf_memory.getvalue() + (
            f'\r\n--{boundary}--\r\n'
        ).encode('utf-8')

        self.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        self.headers['Content-Length'] = str(len(body))

        self.conn.request("POST", url, headers=self.headers, body=body)
        res = self.conn.getresponse()
        data = res.read()

        data = json.loads(data.decode("utf-8"))
        if data["status"]:
            return AddressParser.from_dict(data)
        return None

    def check_ine_image(self, report, image_bytes1, image_bytes2) -> IDResult:
        url = f"/api/v1/services/id?report={report}"
        if image_bytes1 and image_bytes2:
            image_in_memory1 = io.BytesIO(image_bytes1)
            image_in_memory2 = io.BytesIO(image_bytes2)

            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            body = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="front"; filename="image1.jpg"\r\n'
                f'Content-Type: image/jpeg\r\n\r\n'
            ).encode('utf-8') + image_in_memory1.getvalue() + (
                f'\r\n--{boundary}\r\n'
                f'Content-Disposition: form-data; name="back"; filename="image2.jpg"\r\n'
                f'Content-Type: image/jpeg\r\n\r\n'
            ).encode('utf-8') + image_in_memory2.getvalue() + (
                f'\r\n--{boundary}--\r\n'
            ).encode('utf-8')

            self.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
            self.headers['Content-Length'] = str(len(body))

        self.conn.request("POST", url, headers=self.headers, body=body)
        res = self.conn.getresponse()
        data = res.read()

        data = json.loads(data.decode("utf-8"))
        return IDResult.from_dict(data)


class NebuiaFunctions(AbstractClientFunctions):
    nebuia = NebuIAAPI()
    redis = Redis()
    db = None
    session = None

    def __init__(self, db: MongoDB, session):
        NebuiaFunctions.db = db
        NebuiaFunctions.session = session


    @staticmethod
    @tool
    def resend_otp(value: str) -> bool:
        """
        Check email validation

        Args:
            email (str): email from user.

        Returns:
            bool: Valid email.
        """
        report = NebuiaFunctions.redis.get_value("report")
        return NebuiaFunctions.nebuia.send_otp(report=report)
    

    @staticmethod
    @tool
    def check_email_valid(value: str) -> bool:
        """
        Check email validation

        Args:
            value (str): email from user.

        Returns:
            bool: Valid email.
        """
        report = NebuiaFunctions.redis.get_value("report")
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", value)
        if len(emails) > 0:
            report = NebuiaFunctions.redis.get_value("report")
            result = NebuiaFunctions.nebuia.save_email(email=emails[0], report=report)
            if result:
                return NebuiaFunctions.nebuia.send_otp(report=report)
            
        return {"status": False, "message": "Lo siento, por favor sube un documento PDF para poderlo analizar"}
    

    @staticmethod
    @tool
    def check_otp_valid(value: str) -> dict:
        """
        Check email otp validation

        Args:
            code (str): code otp from user.

        Returns:
            dict: status and message.
        """
        report = NebuiaFunctions.redis.get_value("report")
        if re.search(r"[0-9]{6}", value):
            return NebuiaFunctions.nebuia.verify_otp(report=report, code=value)
        return False


    @staticmethod
    @tool
    def check_amount_to_request(value: str) -> bool:
        """
        Check max amount to request.

        Args:
            amount (float): Amount to request.

        Returns:
            bool: Valid amount.
        """
        if value.isnumeric():
            if float(value) > 20_000:
                return False
            else:
                return True
        return False


    @staticmethod
    @tool
    def generic_response(value: str) -> str:
        """
        Get generic response if none of functions match.

        Args:
            msg (str): User generic input.

        Returns:
            str: Generic message.
        """
        return "Estoy aqui para ayudarte"


    @staticmethod
    @tool
    def check_name_valid(value: str) -> str:
        """
        Check name from user input.

        Args:
            name (str): Name of user input.

        Returns:
            float: The current stock price, or None if an error occurs.
        """
        try:
            
            return True
        except Exception as e:
            logger.error(f"Error validating for {value}: {e}")
            return False
    

    @staticmethod
    @tool
    def check_number_valid(value: str) -> bool:
        """
        Get the current stock price for a given symbol.

        Args:
            symbol (str): The stock symbol.

        Returns:
            float: The current stock price, or None if an error occurs.
        """
        try:
            if value.isnumeric():
                if len(value) == 8:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error validating for {value}: {e}")
            return False


    async def check_address_document(self, step_details, client_id):
        file1 = NebuiaFunctions.session.get(step_details.get("images")[0])
        content_type = file1.headers['Content-Type']
        if not self.check_file_content(step_details=step_details, content_type=content_type):
            return {"status": False, "message": "Lo siento, por favor sube un documento PDF para poderlo analizar"}

        file_content = file1.content
        address = NebuiaFunctions.nebuia.check_address_document(
            self.get_to_client(client_id).get("report"), file_content)

        if address is None or not address.status:
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_address_valid")
            return {"status": False, "message": "Lo siento, no pude extraer la dirección del documento proporcionado, intenta con otro documento"}

        extracted_data = f"""Tus datos extraidos fueron:
        Dirección: {address.payload.address[0]}
        Código Postal: {address.payload.zone.cp_id}
        Barrio/Colonia: {address.payload.zone.township}"""

        NebuiaFunctions.db.reset_images_to_step(client_id, "check_address_valid")
        return {"status": True, "message": extracted_data}


    async def check_face_spoofing(self, client_id, file_content):
        spoofing = NebuiaFunctions.nebuia.check_face_spoofing(
            self.get_to_client(client_id).get("report"), file_content)
        if spoofing.status and spoofing.payload.status:
            return {"status": True, "message": "Tu rostro se procesó correctamente"}
        else:
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_face_valid")
            return {"status": False, "message": "Parece que tuvimos un error al procesar tu rostro, inténtalo nuevamente"}


    async def check_face_quality(self, step_details, client_id):
        image_url = step_details.get("images")[0]
        file1 = NebuiaFunctions.session.get(image_url)
        file_type = file1.headers['Content-Type']
        file_content = file1.content

        if not self.check_file_content(step_details=step_details, content_type=file_type):
            return {"status": False, "message": "Parece que no enviaste una imagen, por favor envía la foto de tu rostro"}

        quality = NebuiaFunctions.nebuia.check_face_quality(
            self.get_to_client(client_id).get("report"), file_content)
        if not quality.status:
            return {"status": False, "message": "Parece que tuvimos un error al procesar tu rostro, inténtalo nuevamente"}

        if quality.payload > 68:
            spoofing_result = await self.check_face_spoofing(client_id, file_content)
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_face_valid")
            return spoofing_result
        else:
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_face_valid")
            return {"status": False, "message": "Parece que tu rostro no cumple con nuestro estándar de calidad, por favor tómate otra foto y súbela"}


    async def process_ine(self, step_details, client_id):
        num_images = len(step_details.get("images", []))
        if num_images == 1:
            return {"status": False, "message": "Por favor envía la parte trasera de tu INE"}

        file1 = NebuiaFunctions.session.get(step_details.get("images")[0])
        file2 = NebuiaFunctions.session.get(step_details.get("images")[1])

        content_type1 = file1.headers['Content-Type']
        content_type2 = file2.headers['Content-Type']
        if not self.check_file_content(step_details=step_details, content_type=content_type1) or not self.check_file_content(step_details=step_details, content_type=content_type2):
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_face_valid")
            return {"status": False, "message": "Lo siento, pero los archivos proporcionados deben ser imágenes"}

        result = NebuiaFunctions.nebuia.check_ine_image(self.get_to_client(
            client_id).get("report"), file1.content, file2.content)
        if result.status:
            extracted_data = f"""Tus datos extraidos fueron:
            Nombre: {result.payload.names}
            Clave de elector: {result.payload.extra.elector_key}
            CURP: {result.payload.personal_number}
            Número de documento: {result.payload.document_number}"""
            return {"status": True, "message": extracted_data}
        else:
            NebuiaFunctions.db.reset_images_to_step(client_id, "check_ine_valid")
            return {"status": False, "message": "Lo siento, no pude procesar tu INE, por favor envia de nuevo la parte frontal de tu INE, si tienes dudas puedes consultar nuestro enlace https://docs.NebuiaFunctions.nebuia.com/help/verifications"}
    
    def check_file_content(self, step_details, content_type):
        for type in step_details["accept"]:
            if type == content_type:
                return True
        return False
    
    def get_to_client(self, id_client):
        to = self.db.client_exist(id_client)
        return to
    
    def get_media_tools(self) -> Dict[str, Callable]:
       return {
            "check_address_valid": self.check_address_document,
            "check_face_valid": self.check_face_quality,
            "check_ine_valid": self.process_ine
        }

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        llm_functions = [
            NebuiaFunctions.resend_otp,
            NebuiaFunctions.check_email_valid,
            NebuiaFunctions.check_otp_valid,
            NebuiaFunctions.check_amount_to_request,
            NebuiaFunctions.generic_response,
            NebuiaFunctions.check_name_valid,
            NebuiaFunctions.check_number_valid
        ]

        return [convert_to_openai_tool(f) for f in llm_functions]