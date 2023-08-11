from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ast
import json
from .models import Election, Choice, Voter
from .serializers import (
    ElectionSerializer,
    VoterSerialzer,
    ChoiceSerialzer,
    ElectionUserSerializer,
)

from . import contract_functions

# Create your views here.

# @api_view(["POST"])
# def test(request):
#     received_json_data = json.loads(request.body)
#     w3 = Web3(
#         Web3.HTTPProvider(
#             "https://sepolia.infura.io/v3/ed97a557d0a646669e1640f304c8a111"
#         )
#     )

#     nonce = w3.eth.get_transaction_count(my_address)
#     print(nonce)

#     my_contract = w3.eth.contract(address=contract_address, abi=abi)
#     result = my_contract.functions.compareOurString("Abhshek").call()
#     print(result)

#     call_function = my_contract.functions.updateOurString(
#         received_json_data["newName"]
#     ).build_transaction({"chainId": chain_id, "from": my_address, "nonce": nonce})

#     signed_tx = w3.eth.account.sign_transaction(call_function, private_key=private_key)

#     send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

#     tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

#     print(tx_receipt)

#     return Response(
#         {
#             "status": "Working",
#             "Code": 200,
#             "nonce": nonce,
#             "result": result,
#             "receipt": json.dumps(tx_receipt["transactionHash"].hex(), default=vars),
#         }
#     )


class NewVoter(generics.CreateAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerialzer


@api_view(["POST", "OPTIONS"])  
def login(request):
    received_json_data = json.loads(request.body)
    email_id = received_json_data["email_id"]
    password = received_json_data["password"]
    user_instance = None
    try:
        user_instance = Voter.objects.get(user_email=email_id)
    except:
        return Response(
            {
                "message": "Email not registered.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_instance.password != password:
        return Response(
            {
                "message": "Invalid password.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = VoterSerialzer(user_instance).data
    return Response(data)


@api_view(["POST"])
def identifyVoter(request):
    received_json_data = json.loads(request.body)
    voter = Voter.objects.get(pk=received_json_data["voter_id"])
    data = VoterSerialzer(voter).data
    return Response(data)


@api_view(["POST"])
def newElection(request):
    received_json_data = json.loads(request.body)
    # index = Election.objects.all().count()
    title = received_json_data["title"]
    number_of_choices = received_json_data["number_of_choices"]
    choices = received_json_data["choices"]
    elec = Election(title=title, number_of_choices=number_of_choices)
    elec.save()
    choice_id = 0
    for choice in choices:
        ch = Choice(name=choice, election=elec, choice_id=choice_id)
        ch.save()
        choice_id += 1

    hash = contract_functions.createNewElection(
        election_id=elec.id,
        number_of_choices=elec.number_of_choices,
    )

    election_data = ElectionSerializer(elec).data
    return Response(
        {
            "election": election_data,
            "hash": hash,
        }
    )


@api_view(["POST"])
def getElectionResult(request):
    received_json_data = json.loads(request.body)
    election_id = received_json_data["election_id"]
    election = Election.objects.get(pk=election_id)

    if election.running:
        return Response(
            {
                "message": "The poll is still running!",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = str(contract_functions.getElectionResult(election_id=election_id))
    res = json.loads(result)
    max = -1
    winners = []
    for idx, val in enumerate(res):
        if val > max:
            max = val
            winners = []
            winners.append(idx)
        elif val == max:
            winners.append(idx)

    election = Election.objects.get(pk=election_id)
    choices = election.choices
    choices_data = ChoiceSerialzer(choices, many=True).data
    return Response(
        {
            "choices": choices_data,
            "votes": json.loads(result),
            "winners": winners,
        }
    )


@api_view(["POST"])
def castVote(request):
    received_json_data = json.loads(request.body)
    election_id = received_json_data["election_id"]
    choice_id = received_json_data["choice_id"]
    voter_id = received_json_data["voter_id"]

    election = Election.objects.get(pk=election_id)
    voter = Voter.objects.get(pk=voter_id)
    if election.running == False:
        return Response(
            {
                "message": "The poll is over!",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    hash = contract_functions.vote(election_id=election_id, choice_id=choice_id)
    election.number_of_votes += 1
    voter.voted_in.add(election)
    election.save()
    voter.save()

    return Response(
        {
            "hash": hash,
        }
    )


@api_view(["POST"])
def verifyVote(request):
    received_json_data = json.loads(request.body)
    election_id = received_json_data["election_id"]
    hash = received_json_data["hash"]

    choice_id = contract_functions.verifyVote(election_id=election_id, hash=hash)

    if choice_id == -1:
        return Response(
            {"message": "Invalid Hash!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    election = Election.objects.get(pk=election_id)
    choice = election.choices.get(choice_id=choice_id)
    choice_data = ChoiceSerialzer(choice).data
    return Response(
        {
            "choice": choice_data,
        }
    )


@api_view(["GET"])
def getRunningPolls(request):
    elections = Election.objects.filter(running=True)
    data = ElectionSerializer(elections, many=True).data
    return Response(data)


@api_view(["GET"])
def getClosedPolls(request):
    elections = Election.objects.filter(running=False)
    data = ElectionSerializer(elections, many=True).data
    return Response(data)


@api_view(["POST"])
def closePoll(request):
    received_json_data = json.loads(request.body)
    voter = Voter.objects.get(pk=received_json_data["voter_id"])
    if voter.admin == False:
        return Response(
            {
                "message": "You are not admin!",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    election = Election.objects.get(pk=received_json_data["election_id"])
    election.running = False
    election.save()
    return Response(
        {
            "message": "Poll has been closed.",
        }
    )


@api_view(["POST"])
def searchElection(request):
    received_json_data = json.loads(request.body)
    elections = Election.objects.filter(title__icontains=received_json_data["title"])[
        :5
    ]
    data = ElectionUserSerializer(
        elections,
        many=True,
        context={"voter_id": received_json_data["voter_id"]},
    ).data
    return Response(data)


@api_view(["POST"])
def getElectionforVoter(request):
    received_json_data = json.loads(request.body)
    elections = Election.objects.all()
    data = ElectionUserSerializer(
        elections,
        many=True,
        context={"voter_id": received_json_data["voter_id"]},
    ).data
    return Response(data)


@api_view(["POST"])
def getClosedElectionforVoter(request):
    received_json_data = json.loads(request.body)
    elections = Election.objects.filter(running=False)
    data = ElectionUserSerializer(
        elections,
        many=True,
        context={"voter_id": received_json_data["voter_id"]},
    ).data
    return Response(data)


@api_view(["POST"])
def getOngoingElectionforVoter(request):
    received_json_data = json.loads(request.body)
    elections = Election.objects.filter(running=True)
    data = ElectionUserSerializer(
        elections,
        many=True,
        context={"voter_id": received_json_data["voter_id"]},
    ).data
    return Response(data)


@api_view(["POST"])
def adminLogin(request):
    received_json_data = json.loads(request.body)
    email_id = received_json_data["email_id"]
    password = received_json_data["password"]
    user_instance = None
    try:
        user_instance = Voter.objects.get(user_email=email_id)
    except:
        return Response(
            {
                "message": "Email not registered.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_instance.password != password:
        return Response(
            {
                "message": "Invalid password.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_instance.admin == False:
        return Response(
            {
                "message": "You are not authorised.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = VoterSerialzer(user_instance).data
    return Response(data)

@api_view(["POST"])
def getElection(request):
    received_json_data = json.loads(request.body)
    election = Election.objects.get(pk=received_json_data["election_id"])
    data=ElectionSerializer(election).data
    return Response(data)