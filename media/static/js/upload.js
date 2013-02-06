/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
            paramName: 'image',
            filesContainer: $('#upload_files_container'),
            uploadTemplateId: null,
            downloadTemplateId: null,
            uploadTemplate: function (o) {
                var rows = $();
                $.each(o.files, function (index, file) {
                    var row = $('<li class="template-upload fade">' +
                                    '<div class="preview"><span class="fade"></span></div>' +
                                    '<div class="infos">'+
                                        '<span class="name"></span>' +
                                        '<span class="size"></span>' +
                                    '</div>' +

                                    (file.error ?
                                        '<div class="error" colspan="2"></div>' :
                                    '<div class="start"><button class="PTbutton start">Start</button></div>') +
                                    '<div class="cancel"><button class="PTbutton cancel">Cancel</button></div>' +
                                    '<div class="progress"><div class="bar" style="width:0%;"></div></div>' +
                                '</li>');
                    row.find('.name').text(file.name);
                    row.find('.size').text(o.formatFileSize(file.size));

                    if (file.error) {
                        row.find('.error').text(
                            locale.fileupload.errors[file.error] || file.error
                        );
                    }
                    rows = rows.add(row);
                });
                return rows;
            },
            downloadTemplate: function (o) {
                var rows = $();
                $.each(o.files, function (index, file) {
                     var row = $('<li class="template-download fade">' +
                                    '<div class="preview"><span class="fade"></span></div>' +
                                    '<div class="infos">'+
                                        '<span class="name"></span>' +
                                        '<span class="size"></span>' +
                                    (file.error ?
                                        '<span class="error" colspan="2"></span>' : '' )+
                                    '</div>' +

                                    '<div class="delete"><button class="PTbutton delete">Supprimer</button></div>' +
                                    '<input type="checkbox" name="delete" value="1"></td></tr>' +
                                '</li>');
                    row.find('.size').text(o.formatFileSize(file.size));
                    if (file.error) {
                        row.find('.name').text(file.name);
                        row.find('.error').text(
                            locale.fileupload.errors[file.error] || file.error
                        );
                    } else {
                        row.find('.name a').text(file.name);
                        if (file.thumbnail_url) {
                            row.find('.preview').append('<a><img></a>')
                                .find('img').prop('src', file.thumbnail_url);
                            row.find('a').prop('rel', 'gallery');
                        }
                        row.find('a').prop('href', file.url);
                        row.find('.delete button')
                            .attr('data-type', file.delete_type)
                            .attr('data-url', file.delete_url);
                    }
                    rows = rows.add(row);
                });
                return rows;
            }



        });

    // Enable iframe cross-domain access via redirect option:
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            '/cors/result.html?%s'
        )
    );

    if (window.location.hostname === 'blueimp.github.com') {
        // Demo settings:
        $('#fileupload').fileupload('option', {
            url: '//jquery-file-upload.appspot.com/',
            maxFileSize: 5000000,
            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
            process: [
                {
                    action: 'load',
                    fileTypes: /^image\/(gif|jpeg|png)$/,
                    maxFileSize: 20000000 // 20MB
                },
                {
                    action: 'resize',
                    maxWidth: 1440,
                    maxHeight: 900
                },
                {
                    action: 'save'
                }
            ]
        });
        // Upload server status check for browsers with CORS support:
        if ($.support.cors) {
            $.ajax({
                url: '//jquery-file-upload.appspot.com/',
                type: 'HEAD'
            }).fail(function () {
                $('<span class="alert alert-error"/>')
                    .text('Upload server currently unavailable - ' +
                            new Date())
                    .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $('#fileupload').each(function () {
            var that = this;
            $.getJSON(this.action, function (result) {
                if (result && result.length) {
                    $(that).fileupload('option', 'done')
                        .call(that, null, {result: result});
                }
            });
        });
    }

});
