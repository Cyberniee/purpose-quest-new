export function handlePurchase(productId, productName, productPrice, productPriceId, stripe) {
    // Create a checkout session with the product ID
    console.log("sending this to the api:", productId, productName, productPrice, productPriceId, stripe)
    fetch('/payments/create_checkout_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id_stripe: productId, product_name: productName, product_price: productPrice, product_price_id: productPriceId }),
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (session) {
            // Redirect to Stripe Checkout page
            stripe.redirectToCheckout({ sessionId: session.id });
        })
        .then(function (result) {
            // Handle any errors during checkout
            if (result.error) {
                console.error(result.error.message);
            }
        })
        .catch(function (error) {
            console.error('Error:', error);
        });
}