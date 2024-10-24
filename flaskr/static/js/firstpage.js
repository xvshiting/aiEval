$(document).ready(function(){

$("#sub-btn").click(function(){
    var form_data = new FormData()
    var file_data = $("#fileselect").prop("files")[0]
    form_data.append('file', file_data)
    var group_name = $("#groupname").val()
    var group_tag = $("#gametag").val()
    if (group_name==""){
        alert("组名不能为空！");
        return 

    }
    if ($("#fileselect").prop("files").length<=0){
        alert("未选择上传文件！");
        return  
    }
    $("#sub-btn").toggle();
    $("#submit_warning_div").toggle();
    
    console.log(group_name)
    console.log(group_tag)
    form_data.append("groupname",group_name)
    form_data.append("gametag",group_tag)
    $.ajax({
        url: "/submitpred",
        type: 'POST',
        data: form_data, // 将JavaScript对象转换为JSON字符串
        contentType: false,
        processData: false,
        success: function(data) {
            console.log(data) //["总体情况"])
            data = JSON.parse(data)
            if (data["status"]!="ok"){
                alert(data["msg"])
            }
            else{
                console.log(data["data"]["score"])
                $("#score_span").text(data["data"]["score"]);
                $("#submit_warning_div").toggle()
                $("#score_div").toggle();
            }

        },
        error: function(xhr, status, error) {
            console.error("An error occurred: " + status + "\nError: " + error);
        }
    });


    });



})