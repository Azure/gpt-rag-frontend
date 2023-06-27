import Cookie from 'universal-cookie';

export async function getTokenOrRefresh() {
    const cookie = new Cookie();
    const speechToken = cookie.get('speech-token');

    if (speechToken === undefined) {
        try {
            const res = await fetch("/api/get-speech-token", {
                method: "GET"
            });
            const response = await res.json();
            const token = response.token;
            const region = response.region;
            const speechRecognitionLanguage = response.speechRecognitionLanguage;
            const speechSynthesisLanguage = response.speechSynthesisLanguage;
            const speechSynthesisVoiceName = response.speechSynthesisVoiceName;
            cookie.set('speech-token', region + ':' + token + ':' + speechRecognitionLanguage + ':' + speechSynthesisLanguage + ':' + speechSynthesisVoiceName, {maxAge: 540, path: '/'});

            console.log('Token fetched from back-end: ' + token);
            return { authToken: token, region: region, speechRecognitionLanguage: speechRecognitionLanguage, speechSynthesisLanguage: speechSynthesisLanguage, speechSynthesisVoiceName: speechSynthesisVoiceName };
        } catch (err) {
            console.log(err);
            return { authToken: null, error: err };
        }
    } else {
        console.log('Token fetched from cookie: ' + speechToken);
        const params = speechToken.split(':');
        return { authToken: params[1], region: params[0], speechRecognitionLanguage: params[2], speechSynthesisLanguage: params[3], speechSynthesisVoiceName: params[4]  };
    }
}