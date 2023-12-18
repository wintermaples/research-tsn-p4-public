#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define NETLINK_ID 22

struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh = NULL;
struct iovec iov;
int sock_fd;
struct msghdr msg;

int main(int argc, char *argv[])
{
    int ifindex = 2;
    unsigned char payload[] = {
        80,
        135,
        137,
        214,
        81,
        179,
        4,
        124,
        22,
        138,
        236,
        0,
        8,
        0,
        69,
        0,
        0,
        29,
        50,
        32,
        64,
        0,
        64,
        17,
        109,
        214,
        192,
        168,
        0,
        136,
        192,
        168,
        25,
        1,
        183,
        171,
        78,
        33,
        0,
        9,
        154,
        244,
        0,
        1,
        2
    };
    int payload_len = sizeof(payload);
    size_t packet_size = sizeof(ifindex) + sizeof(payload_len) + sizeof(payload);

    sock_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ID);

    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid();
    bind(sock_fd, (struct sockaddr *)&src_addr, sizeof(src_addr));

    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0;
    dest_addr.nl_groups = 0;

    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(packet_size));
    memset(nlh, 0, NLMSG_SPACE(packet_size));
    nlh->nlmsg_len = NLMSG_SPACE(packet_size);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;

    memcpy(NLMSG_DATA(nlh), &ifindex, sizeof(int));
    memcpy(NLMSG_DATA(nlh) + sizeof(int), &payload_len, sizeof(int));
    memcpy(NLMSG_DATA(nlh) + sizeof(int) + sizeof(int), payload, sizeof(payload));

    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    sendmsg(sock_fd, &msg, 0);

    return 0;
}