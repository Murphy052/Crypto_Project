const getServerPublicKeys = function() {
    fetch(`http://localhost:8000/kdc/public-key/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse the JSON response
        })
        .then(data => {
            // Extract relevant data from the response
            const publicKeys = {
                e: data.public_key_exp,
                n: data.public_key_n
            };
            // Convert the data to JSON string
            const jsonString = JSON.stringify(publicKeys);
            // Store the JSON string in local storage
            localStorage.setItem('serverPublicKeys', jsonString);
            // console.log('Public keys data stored in local storage:', publicKeys);
        })
        .catch(error => {
            // Handle errors
            console.error('There was a problem with the fetch operation:', error);
        });
}

getServerPublicKeys();