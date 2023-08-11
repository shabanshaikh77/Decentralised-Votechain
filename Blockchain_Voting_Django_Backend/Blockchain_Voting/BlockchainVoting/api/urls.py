from django.urls import path
from api import views

urlpatterns = [
    # path("test/", views.test),
    path("createVoter/", views.NewVoter.as_view()),
    path("login/", views.login),
    path("adminLogin/", views.adminLogin),
    path("createNewElection/", views.newElection),
    path("getElectionResult/", views.getElectionResult),
    path("castVote/", views.castVote),
    path("verifyVote/", views.verifyVote),
    path("getRunningPolls/", views.getRunningPolls),
    path("getClosedPolls/", views.getClosedPolls),
    path("searchElection/", views.searchElection),
    path("identifyVoter/", views.identifyVoter),
    path("getVoterElections/", views.getElectionforVoter),
    path("getClosedVoterElections/", views.getClosedElectionforVoter),
    path("getOngoingVOterElections/", views.getOngoingElectionforVoter),
    path("closePoll/", views.closePoll),
    path("getElection/", views.getElection),
]
