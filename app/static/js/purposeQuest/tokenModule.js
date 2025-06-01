let tokenId = null;
let productSlug = null;

export function setTokenId(value) {
    tokenId = value;
    // console.log("tokenModel set tokenId to: ", tokenId)
}

export function getTokenId() {
    // console.log("tokenModel retrieved tokenId: ", tokenId)
    return tokenId;
}

export function setProductSlug(value) {
    productSlug = value;
    // console.log("tokenModel set productSlug to: ", productSlug)
}

export function getProductSlug() {
    // console.log("tokenModel retrieved productSlug: ", productSlug)
    return productSlug;
}
