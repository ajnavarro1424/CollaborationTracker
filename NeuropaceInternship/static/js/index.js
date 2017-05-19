$(document).ready(function(){
		$("#collab_table, #audit-table, #search_table").tablesorter({
			// this will apply the bootstrap theme if "uitheme" widget is included
			// the widgetOptions.uitheme is no longer required to be set
			theme : "bootstrap",
			widthFixed: false,
			headerTemplate : '{content} {icon}', // new in v2.7. Needed to add the bootstrap icon!
			// widget code contained in the jquery.tablesorter.widgets.js file
			// use the zebra stripe widget if you plan on hiding any rows (filter widget)
			widgets : [ "uitheme", "filter", "zebra" ],
			widgetOptions : {
				// using the default zebra striping class name, so it actually isn't included in the theme variable above
				// this is ONLY needed for bootstrap theming if you are using the filter widget, because rows are hidden
				zebra : ["even", "odd"],
				// class names added to columns when sorted
				columns: [ "primary", "secondary", "tertiary" ],
				// reset filters button
				filter_reset : ".reset",
				// extra css class name (string or array) added to the filter element (input or select)
				filter_cssFilter: "form-control"
			}
		});
		// Reset table function defined for the reset sort/filter buttons
		$('.reset').click(function(){
			$('table').trigger('sortReset');
			$('table').trigger('filterReset');
			return false;
		});



		$('.btn-archive').click(function(){
			$.post("/archive",
						  {collab_id : $(this).attr('id').split("_").pop() },
							function(data, status){
								var collab_row = $("#archive_"+ data.collab_id).closest("tr");
								if (data.success) {
									collab_row.remove();
									$("#ajax_flash_msg")
										.html("<p>Successfully archived " + data.new_new_tag + "</p>");
								}
							}
						);
		});

});