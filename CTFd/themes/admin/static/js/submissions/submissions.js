// TODO: Replace this with CTFd JS library
$(document).ready(function () {
    $('.delete-correct-submission').click(function () {
        var elem = $(this).parent().parent();
        var chal = elem.find('.chal').attr('id');
        var chal_name = elem.find('.chal').text().trim();
        var team = elem.find('.team').attr('id');
        var team_name = elem.find('.team').text().trim();
        var key_id = elem.find('.flag').attr('id');

        var td_row = $(this).parent().parent();

        ezq({
            title: 'Delete Submission',
            body: "Are you sure you want to delete correct submission from {0} for challenge {1}".format(
                "<strong>" + htmlentities(team_name) + "</strong>",
                "<strong>" + htmlentities(chal_name) + "</strong>"
            ),
            success: function () {
                var route = script_root + '/api/v1/submissions/' + key_id;
                $.delete(route, function (response) {
                    if (response.success) {
                        td_row.remove();
                    }
                });
            }
        });
    });
});
$(document).ready(function () {
$('.change-type').click(function () {
    var elem = $(this).parent().parent();
    var chal = elem.find('.chal').attr('id');      
    var chal_name = elem.find('.chal').text().trim();
    var team = elem.find('.team').attr('id');
    var team_name = elem.find('.team').text().trim();
    var key_id = elem.find('.flag').attr('id');

    var type_value = elem.find('.subType').text().trim();
    var type_awards = elem.find('.subPoints').text().trim();
    var td_row = $(this).parent().parent();

    ezq({
        title: 'Mark As Answer',
        body: "Are you sure you want to mark this submission from {0} as a solution for challenge {1}".format(
            "<strong>" + htmlentities(team_name) + "</strong>",
            "<strong>" + htmlentities(chal_name) + "</strong>"
        ),
        success: function () {
            var route = script_root + '/api/v1/submissions/' + key_id;
            $.patch(route, function (response) {
                if (response.success) {
                    alert("Changed submission Type " + type_value);
                }
            });
        }
    });
});
});