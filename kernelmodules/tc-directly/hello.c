#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/netdevice.h>
#include <linux/skbuff.h>
#include <linux/inetdevice.h>
#include <linux/netlink.h>
#include <net/sock.h>
#include <linux/if_ether.h>

struct netdev_name_node {
	struct hlist_node hlist;
	struct list_head list;
	struct net_device *dev;
	const char *name;
};

#define NETLINK_ID 22

static struct sock *nl_sock;

static void send_packet(struct net_device *dev, unsigned char *data, int data_len) {
    struct sk_buff *skb;
    struct ethhdr *ethh;

    skb = dev_alloc_skb(ETH_HLEN + data_len);
    if (!skb) {
        pr_err("Failed to allocate skb\n");
        kfree_skb(skb);
        return;
    }

    skb_reserve(skb, ETH_HLEN);
    skb_put(skb, data_len);
    skb_set_network_header(skb, sizeof(*ethh));

    memcpy(skb->data, data, data_len);

    skb->dev = dev;
    skb->protocol = htons(ETH_P_802_3);

    dev_queue_xmit(skb);
}

static void nl_recv_msg(struct sk_buff *skb) {
    struct nlmsghdr *nlh;
    int msg_len;
    unsigned char *msg;

    int ifindex;
    struct net_device *dev;

    int payload_len;
    unsigned char *payload;

    nlh = (struct nlmsghdr *)skb->data;
    msg_len = nlh->nlmsg_len - NLMSG_HDRLEN;
    msg = (unsigned char*) kmalloc(msg_len, GFP_ATOMIC);
    memcpy(msg, nlmsg_data(nlh), msg_len);

    // Extract Interface
    memcpy(&ifindex, msg, sizeof(int));
    dev = dev_get_by_index(&init_net, ifindex);

    // Extract Payload Length
    memcpy(&payload_len, msg + sizeof(int), sizeof(int));

    // Extract Payload
    payload = (unsigned char*) kmalloc(payload_len, GFP_ATOMIC);
    memcpy(payload, msg + sizeof(int) + sizeof(int), payload_len);

    if (dev == NULL) {
        // Debug only.
        printk(KERN_WARNING "A device(Interface Index=%d) is not found.", ifindex);
        return;
    }

    // printk("%s", "=====\n");
    // printk("IFINDEX: %d\n", ifindex);
    // printk("DEV POINTER: %d\n", dev);

    // struct netdev_name_node *name_node;
    // name_node = dev->name_node;
    // printk("%s\n", name_node->name);
    
    // printk("DATA SIZE: %d\n", payload_len);
    // printk("DATA: %s\n", payload);
    // printk("%s", "=====\n");
    
    send_packet(dev, payload, payload_len);

    kfree(msg);
    kfree(payload);
}

struct netlink_kernel_cfg cfg = {
    .input = nl_recv_msg,
};

static int __init mymodule_init(void) {
    pr_info("Module loaded\n");
    nl_sock = netlink_kernel_create(&init_net, NETLINK_ID, &cfg);
    return 0;
}

static void __exit mymodule_exit(void) {
    pr_info("Module unloaded\n");
}

module_init(mymodule_init);
module_exit(mymodule_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Custom Kernel Module");
