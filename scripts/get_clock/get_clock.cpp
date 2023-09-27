#include <iostream>
#include <time.h>
#include <unistd.h>

void gettime(int clock_id, long* sec, long* nsec)
{
    struct timespec gettime_now;
    clock_gettime(clock_id, &gettime_now);
    *sec = gettime_now.tv_sec;
    *nsec = gettime_now.tv_nsec;
}

int main()
{
    long sec = 0;
    long nsec = 0;

    long prevSec = 0;
    long prevNSec = 0;

    long diff = 0;
    long diffFixed = 0;

    while (true) {
        gettime(11, &sec, &nsec); 
        
        diff = (sec - prevSec) * 1000 * 1000 * 1000 + (nsec - prevNSec);
        diffFixed = diff - 1000 * 1000 * 100;
        if (-3000 > diffFixed || diffFixed > 3000) {
            std::cout << sec << std::endl;      // Second of CLOCK_TAI 
            std::cout << nsec << std::endl;      // Nano Second of CLOCK_TAI
            std::cout << diffFixed << std::endl;
            std::cout << "=====" << std::endl;
        }

        gettime(11, &sec, &nsec);
        prevSec = sec;
        prevNSec = nsec;

        usleep(1000 * 100);
    }

    return 0;
}
