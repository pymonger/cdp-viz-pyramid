/**
 * The function to call when the response from the server was a failed
 * attempt (load in this case), or when an error occurred in the Ajax
 * communication. The function is passed the following parameters:
 * @param {Ext.form.BasicForm} form The form that requested the action.
 * @param {Ext.form.Action} action The Action class.
 * If an Ajax error occurred, the failure type will be in failureType.
 * The result property of this object may be examined to perform custom postprocessing.
 *
 * A failed attempt (load in this case) response from the server will be:
 * {success: false, message: 'Failure message to be displayed.'}
 */
function loadFailed(form, action) {

    var failureMessage = "Error occurred trying to retrieve data.";

    // Failure type returned when no field values are returned in the
    // response's data property or the successProperty value is false.
    if (action.failureType == Ext.form.Action.LOAD_FAILURE) {

        // Error on the server side will include an error message in
        // the response.             

        // Decodes (parses) a JSON string to an object. If the JSON is invalid,
        // this function throws a SyntaxError.
        var object = Ext.util.JSON.decode(action.response.responseText);

        failureMessage = object.person.message;
    }
    // Failure type returned when a communication error happens when
    // attempting to send a request to the remote server.
    else if (action.failureType == Ext.form.Action.CONNECT_FAILURE) {
        // The XMLHttpRequest object containing the
        // response data. See http://www.w3.org/TR/XMLHttpRequest/ for
        // details about accessing elements of the response.
        failureMessage = "Please contact support with the following:<br/><br/>" +
            "Status: " + action.response.status +
            "<br/>Status Text: " + action.response.statusText;
    }
    Ext.Msg.alert('Error Message', failureMessage);
}

/**
 * Handle an unsuccessful connection or http request to the server.
 * This has nothing to do with the response from the application.
 * @param {Object} response The XMLHttpRequest object containing the
 *          response data. See [http://www.w3.org/TR/XMLHttpRequest/] for
 *          details about accessing elements of the response.
 * @param {Object} options The parameter to the request call.
 */
function requestFailed(response, options) {

    // The request to the server was unsuccessful.
    //console.log("requestFailed() response object: ", response);
    var paramsStr = "";
    for (p in options.params) {
        paramsStr += "<br/>" + p + "=" + options.params[p];
    }
    Ext.Msg.alert('Error Message',
        "Please contact support with the following:<br/><br/>" +
        "Status: " + response.status +
        "<br/>Status Text: " + response.statusText +
        "<br/>Url: " + options.url +
        "<br/>Params: " + paramsStr +
        "<br/>Response Text:<br/>" + response.responseText);
}

function delquote(str) {
    //remove quotes or double quotes around a string
    return (str=str.replace(/["']{1}/gi,""));
}
