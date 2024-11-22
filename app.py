from flask import Flask, render_template, request, redirect, url_for, jsonify
from verizon.models.account_device_list_request import AccountDeviceListRequest
from verizon.models.account_device_list_result import AccountDeviceListResult
from verizon.models.account_details import AccountDetails
from verizon.models.account_device_list import AccountDeviceList
from verizon.models.carrier_activate_request import CarrierActivateRequest
from verizon.models.device_id import DeviceId
from verizon.models.device_management_result import DeviceManagementResult
from verizon.models.log_in_request import LogInRequest
from verizon.exceptions.connectivity_management_result_exception import ConnectivityManagementResultException
from verizon.exceptions.api_exception import APIException
from verizon.http.auth.thingspace_oauth import ThingspaceOauthCredentials
from verizon.http.auth.vz_m2m_token import VZM2mTokenCredentials
from verizon.models.log_in_result import LogInResult
from verizon.models.oauth_token import OauthToken
from verizon.configuration import Environment
from verizon.verizon_client import VerizonClient

def _oauth_token_provider(last_oauth_token, auth_manager):
    # Add the callback handler to provide a new OAuth token
    # It will be triggered whenever the last provided o_auth_token is null or expired
    oauth_token = None
    if oauth_token is None:
        oauth_token = auth_manager.fetch_token()
    return oauth_token

app = Flask(__name__)
client = None
client_id = None
client_secret = None

# Route for the first page (Access Token)
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to handle access token generation
@app.route('/generate-access-token', methods=['POST'])
def generate_access_token():
    global client, client_id, client_secret
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')

    # Mocking token generation logic (replace with actual API call if needed)
    if client_id and client_secret:
        try:
            # Initialize the Verizon client
            client = VerizonClient(
                thingspace_oauth_credentials=ThingspaceOauthCredentials(
                    oauth_client_id=client_id,
                    oauth_client_secret=client_secret,
                    oauth_token_provider=_oauth_token_provider
                ),
                environment=Environment.PRODUCTION
            )
        except APIException as e:
            return jsonify({"status": "error", "message": e}), 401
        # Simulate token generation success
        return jsonify({"status": "success", "access_token": "mock_access_token"}), 201
    else:
        return jsonify({"status": "error", "message": "Client ID and Client Secret are required"}), 400

# Route for the second page (Session Token)
@app.route('/session-token')
def session_token_page():
    return render_template('session-token.html')

# Endpoint to handle session token generation
@app.route('/generate-session-token', methods=['POST'])
def generate_session_token():
    global client, client_id, client_secret
    username = request.form.get('uws_username')
    password = request.form.get('uws_password')

    # Mocking session token generation logic (replace with actual API call if needed)
    if username and password:
        session_management_controller = client.session_management
        body = LogInRequest(
            username='apimatic.uws',
            password='WeL0v3APIs!'
        )

        try:
            sessionTokenResponse = session_management_controller.start_connectivity_management_session(
                body=body
            )

        except ConnectivityManagementResultException as e: 
            return jsonify({"status": "error", "message": e}), 400
        except APIException as e: 
            return jsonify({"status": "error", "message": e}), 400
        # Simulate session token generation success
        vzm2mToken = sessionTokenResponse.body.session_token 
        client = VerizonClient(
            thingspace_oauth_credentials=ThingspaceOauthCredentials(
                oauth_client_id=client_id,
                oauth_client_secret=client_secret
            ),
            vz_m2m_token_credentials=VZM2mTokenCredentials(
                vz_m2m_token=vzm2mToken
            ),
            environment=Environment.PRODUCTION
        )
        return jsonify({"status": "success", "session_token": vzm2mToken}), 201
    else:
        return jsonify({"status": "error", "message": "Username and Password are required"}), 400

# Route for the third page (Actions)
@app.route('/actions')
def actions_page():
    return render_template('actions.html')

# Route for the Output page (Output)
@app.route('/result', methods=['GET'])
def result_page():
    data = request.args.to_dict()
    return render_template('result.html', data=data)

# Endpoint to handle list service plans
@app.route('/get-service-plans', methods=['POST'])
def get_service_plans():
    global client
    data = {
        "action": "List Service Plans",
    }
    accoutName = request.form.get('account_name')
    if accoutName:
        service_plans_controller = client.service_plans
        try:
            result = service_plans_controller.list_account_service_plans(accoutName)
            data["items"] = result.text
        except ConnectivityManagementResultException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        except APIException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        return jsonify({"status": "success", "data": data}), 200
    else:
        return jsonify({"status": "error", "message": "Bad Request!"}), 400

# Endpoint to handle list device info
@app.route('/get-device-info', methods=['POST'])
def get_device_info():
    global client
    data = {
        "action": "List Device Information",
    }
    deviceId = request.form.get('device_id')
    deviceKind = request.form.get('device_kind')
    if deviceId and deviceKind:
        device_management_controller = client.device_management
        body = AccountDeviceListRequest(
            device_id=DeviceId(
                id=deviceId,
                kind=deviceKind
            )
        )
        try:
            result = device_management_controller.list_devices_information(body)
            data["items"] = result.text
        except ConnectivityManagementResultException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        except APIException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        return jsonify({"status": "success", "data": data}), 200
    else:
        return jsonify({"status": "error", "message": "Bad Request!"}), 400

# Endpoint to handle activate device
@app.route('/activate-device', methods=['POST'])
def activate_device():
    global client
    data = {
        "action": "Acitivate Device",
    }
    
    if request.form.get('device_id') and request.form.get('device_kind'):
        device_management_controller = client.device_management
        body = CarrierActivateRequest(
            devices=[
                AccountDeviceList(
                    device_ids=[
                        DeviceId(
                            id=request.form.get('device_id'),
                            kind=request.form.get('device_kind')
                        )
                    ]
                )
            ],
            service_plan=request.form.get('service_plan'),
            mdn_zip_code=request.form.get('mdn_zip_code'),
            account_name=request.form.get('account_name'),
            sku_number=request.form.get('sku_number'),
        )

        try:
            result = device_management_controller.activate_service_for_devices(body)
            data["items"] = result.text
        except ConnectivityManagementResultException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        except APIException as e: 
            print(e)
            return jsonify({"status": "success", "error": e}), 400
        return jsonify({"status": "success", "data": data}), 200
    else:
        return jsonify({"status": "error", "message": "Bad Request!"}), 400

if __name__ == '__main__':
    app.run(debug=True)