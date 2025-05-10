function convert_pub_key(public_key) {
    let ans=public_key.slice(43, 36);
    return ans;
}