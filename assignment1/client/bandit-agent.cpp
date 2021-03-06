#include <iostream>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <math.h>
#include <vector>
#include <random>

#include "gsl/gsl_rng.h"
#include "gsl/gsl_randist.h"
#include "beta_distribution.h"

#define MAXHOSTNAME 256

using namespace std;

void options(){
    cout << "Usage:\n";
    cout << "bandit-agent\n"; 
    cout << "\t[--numArms numArms]\n";
    cout << "\t[--randomSeed randomSeed]\n";
    cout << "\t[--horizon horizon]\n";
    cout << "\t[--explorationHorizon explorationHorizon]\n";
    cout << "\t[--hostname hostname]\n";
    cout << "\t[--port port]\n";
}

/*
  Read command line arguments, and set the ones that are passed (the others remain default.)
*/
bool setRunParameters(int argc, char *argv[], int &numArms, int &randomSeed, unsigned long int &horizon,unsigned long int &explorationHorizon, string & hostname, int &port){

    int ctr = 1;
    while(ctr < argc){

        //cout << string(argv[ctr]) << "\n";

        if(string(argv[ctr]) == "--help"){
            return false;//This should print options and exit.
        }
        else if(string(argv[ctr]) == "--numArms"){
            if(ctr == (argc - 1)){
                return false;
            }
            numArms = atoi(string(argv[ctr + 1]).c_str());
            ctr++;
        }
        else if(string(argv[ctr]) == "--randomSeed"){
            if(ctr == (argc - 1)){
                return false;
            }
            randomSeed = atoi(string(argv[ctr + 1]).c_str());
            ctr++;
        }
        else if(string(argv[ctr]) == "--horizon"){
            if(ctr == (argc - 1)){
                return false;
            }
            horizon = atoi(string(argv[ctr + 1]).c_str());
            ctr++;
        }
        else if(string(argv[ctr]) == "--explorationHorizon"){
            if(ctr == (argc - 1)){
                return false;
            }
            explorationHorizon = atoi(string(argv[ctr + 1]).c_str());
            ctr++;
        }
        else if(string(argv[ctr]) == "--hostname"){
            if(ctr == (argc - 1)){
                return false;
            }
            hostname = string(argv[ctr + 1]);
            ctr++;
        }
        else if(string(argv[ctr]) == "--port"){
            if(ctr == (argc - 1)){
                return false;
            }
            port = atoi(string(argv[ctr + 1]).c_str());
            ctr++;
        }
        else{
            return false;
        }

        ctr++;
    
    }
    return true;
}

vector<int> S_i, F_i;

int thompson(int numArms){
    // This function returns arm to be sampeled
    // This is used to generate random number and hence the best arm
    // http://stackoverflow.com/questions/15165202/random-number-generator-with-beta-distribution
    // Used code from here^ to do sampling from beta distribution
    std::random_device rd;
    std::mt19937 genRnd(rd());

    float bestSample = -1, bestArm = 0;

    for(int i=0;i<numArms;i++){
        sftrabbit::beta_distribution<> beta(2*(S_i[i]+1), 2*(F_i[i]+1));
        float betaSample = beta(genRnd); 
        if(betaSample>bestSample){
            bestSample = betaSample; 
            bestArm = i;  
        }  
    } 
    return bestArm;
}

int main(int argc, char *argv[]){
    // Run Parameter defaults.
    int numArms = 5;
    int randomSeed = time(0);
    unsigned long int horizon = 200;
    unsigned long int explorationHorizon=200;
    string hostname = "localhost";
    int port = 5000;

    //Set from command line, if any.
    if(!(setRunParameters(argc, argv, numArms, randomSeed, horizon, explorationHorizon, hostname, port))){
        //Error parsing command line.
        options();
        return 1;
    }

    struct sockaddr_in remoteSocketInfo;
    struct hostent *hPtr;
    int socketHandle;

    bzero(&remoteSocketInfo, sizeof(sockaddr_in));
  
    if((hPtr = gethostbyname((char*)(hostname.c_str()))) == NULL){
        cerr << "System DNS name resolution not configured properly." << "\n";
        cerr << "Error number: " << ECONNREFUSED << "\n";
        exit(EXIT_FAILURE);
    }

    if((socketHandle = socket(AF_INET, SOCK_STREAM, 0)) < 0){
        close(socketHandle);
        exit(EXIT_FAILURE);
    }

    memcpy((char *)&remoteSocketInfo.sin_addr, hPtr->h_addr, hPtr->h_length);
    remoteSocketInfo.sin_family = AF_INET;
    remoteSocketInfo.sin_port = htons((u_short)port);

    if(connect(socketHandle, (struct sockaddr *)&remoteSocketInfo, sizeof(sockaddr_in)) < 0){
        //code added
        cout<<"connection problem"<<".\n";
        close(socketHandle);
        exit(EXIT_FAILURE);
    }

    char sendBuf[256];
    char recvBuf[256];

    for(int i=0;i<numArms;i++){
        S_i.push_back(0);
        F_i.push_back(0);
    }    

    int armToPull = thompson(numArms);
    sprintf(sendBuf, "%d", armToPull);
    cout << "Sending action " << armToPull << ".\n";

    while(send(socketHandle, sendBuf, strlen(sendBuf)+1, MSG_NOSIGNAL) >= 0){
        int reward = 0;
        unsigned long int pulls=0;
        char temp;

        recv(socketHandle, recvBuf, 256, 0);
        sscanf(recvBuf, "%d %c %lu", &reward, &temp, &pulls);
        cout << "Received reward " << reward << ".\n";

        if(reward == 1)
            S_i[armToPull] += 1;
        else
            F_i[armToPull] += 1;

        armToPull = thompson(numArms);
        sprintf(sendBuf, "%d", armToPull);
        cout << "Sending action " << armToPull << ".\n";
    }

    close(socketHandle);
    cout << "Terminating.\n";

    return 0;
}
          
