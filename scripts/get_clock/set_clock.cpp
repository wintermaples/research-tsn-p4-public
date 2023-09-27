#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <iostream>

int main( void )
{
    struct timespec stime;

    if( clock_gettime( CLOCK_REALTIME, &stime) == -1 ) {
        perror( "getclock" );
        std::cout << "Failure" << std::endl;
        exit( EXIT_FAILURE );
    }

    stime.tv_sec -= (60*60)*24*1000L;
    stime.tv_nsec = 0;

    if( clock_settime( CLOCK_REALTIME, &stime) == -1 ) {
        perror( "setclock" );
        std::cout << "Failure" << std::endl;
        exit( EXIT_FAILURE );
    }

    return ( EXIT_SUCCESS );
}