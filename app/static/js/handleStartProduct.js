export function startProduct(tokenId) {
    if (!tokenId) {
        console.error("Missing tokenId");
        return;
    }

    // Just redirect to the token-based route
    window.location.href = `/product/${tokenId}`;
}