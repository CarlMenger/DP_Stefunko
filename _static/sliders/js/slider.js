var slidersDiv = $("#slidersDiv");


var sliders = $("#sliders .slider");


sliders.each(function () {
    var value = parseInt($(this).text(), 10),
        availableTotal = 100;


    $(this).empty().slider({
        value: 0,
        min: 0,
        max: 100,
        range: "max",
        step: 1,
        animate: 100,
        change: function (event, ui){
            var totalDiv = 0;

            sliders.not(this).each(function () {
                totalDiv += $(this).slider("option", "value");
                $("#currentPercentage").empty().text(totalDiv.toString());

            });
        },
        slide: function (event, ui) {

            // Get current total
            var total = 0;

            sliders.not(this).each(function () {
                total += $(this).slider("option", "value");
                $("#currentPercentage").empty().text(total.toString());

            });


            var max = availableTotal - total;
            if (max - ui.value >= 0) {
                // Need to do this because apparently jQ UI
                // does not update value until this event completes
                total += ui.value;
                console.log(max - ui.value);
                $(this).siblings().text(ui.value);

            } else {
                return false;
            }


            if (total < 100) {
                $("#continue_button").hide()
            } else {
                $("#continue_button").show()
            }

        }
    });
});

