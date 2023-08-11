// SPDX-License-Identifier: MIT

pragma solidity ^0.8.9;

contract Ballot{
    struct Contender{
        uint votes;
    }

    struct Election{
        mapping(uint=>Contender) choices;
        uint number_of_choices;
        mapping(string=>int) verify;
    }

    mapping(uint=>Election) elections;

    function createNewElection(uint election_id,uint choices_count) public{
        Election storage newElection = elections[election_id];
        newElection.number_of_choices = choices_count;
    }

    function vote(uint election_id,uint choice_id) public{
        elections[election_id].choices[choice_id].votes++;
    }

    function hashVote(uint election_id,int choice_id,string memory hash)public{
        if(choice_id==0){
            choice_id=-1;
        }
        elections[election_id].verify[hash]=choice_id;
    }

    function verifyVote(uint election_id,string memory hash)public view returns (int){
        int ans =  elections[election_id].verify[hash];
        if(ans==0){
            return -1;
        }
        else if(ans==-1){
            return 0;
        }
        else{
            return ans;
        }
    }

    function getElectionResult(uint election_id)public view returns (uint[] memory){
        uint[] memory ans = new uint[](elections[election_id].number_of_choices);
        for(uint i=0;i<elections[election_id].number_of_choices;i++)
        {
            ans[i]=elections[election_id].choices[i].votes;
        }
        return ans;
    }
}

