connect [ip server] port [port server] : kết nối đến server với ip server và port server đang mở.
close hoặc disconnect: kết thúc hoặc đóng kết nối với server.

login [username]: login server với tài khoản của user, sau dòng này hiện lệnh nhập password (chú ý: password không được hiện ra khi người dùng nhập).
ví dụ:
login legon
>> password: *******
Login successfully or Wellcome legon login to server.
register [username]: đăng ký tài khoản mới, sau dòng này hiện dòng bắt người dùng nhập password (chú ý: password không được hiện ra khi người dùng nhập).
ví dụ: 
register legon
>> password: *******
Register successfully
change_password [username]: yêu cầu đổi password mới của user, sau lệnh này bắt người dùng nhập password cũ, nếu password cũng nhập đúng thì hiện dòng tiếp theo yêu cầu nhập password mới (chú ý: password không được hiện ra khi người dùng nhập)
ví dụ: 
change_password legon
>> password: *******
>> new password: *******
Change password successfully
Chú ý: với lệnh register, login, change_password thì password từ phía người dùng nhập vào và gửi cho server chưa được mã hóa.
Các option của các lệnh register, login, change_password:
–encrypt: yêu cầu mã hóa dữ liệu trước khi gửi cho server (bao gồm username và password của người dùng)
Ví dụ:
login – encrypt Hans
>> password: *******
check_user [-option] [username]: kiểm tra thông tin của username, bao gồm các option sau:
–find: kiểm tra user có tồn tại trong database
–online: kiểm tra user có online hay không?
–show_date: hiện ngày sinh của user (dd/mm/yyyy)
–show_name: hiện tên của user
–show_note: hiện ghi chú của user
–show: hiện tất cả thông tin cá nhân của user
Ví dụ: 	check_user –online Hans
		>>User is online
		check_user –show_date Hans
		>> Birthday of Hans is 07/08/2000
setup_info [-option] [username]: thiết lập hoặc thay đổi thông tin cá nhân của user, gồm có các option sau:
–name [Chuỗi tên]: tên của user
–date [birthday]: ngày sinh của user (dd/mm/yyyy)
–note [chuỗi ghi chú]: ghi chú của user
Ví dụ: 	setup_info –name “Nguyen Van A” Hans
		>>Name of Hans is “Nguyen Van A”
		setup_info –date 07/08/2000 Hans
		>>Birthday of Hans is 07/08/2000
Chức năng upload, download dữ liệu (hỗ trợ được hết các loại tập tin: văn bản, ảnh, video). Gồm các lệnh sau:
upload [-option] [filename]: thực hiện upload dữ liệu lên server. 
–change_name [new filename]: đổi tên file thành tên mới. Ví dụ: upload –change_name new_name.docx laptrinhmang.docx (upload file laptrinhmang.docx lên server với tên mới là new_name.docx).
–multi_file [list filename]: thực hiện upload nhiều file lên server, ví dụ: upload –multi_file text1.doc abc.bmp laptrinhmang.docx
–encrypt_data: thực hiện upload file với nội dung đã được mã hóa. Ví dụ: upload –encrypt_data laptrinhmang.docx
download [-option] [filename]: thực hiện download dữ liệu lên server. Trước khi download, phải đảm bảo file dữ liệu có trên server, nếu không thì thông báo file không tồn tại. Sau khi download, file sẽ lưu tại thư mục hiện tại trên Client.
–multi_file: thực hiện dowload nhiều file từ server, ví dụ: download – multi_file text1.doc abc.bmp laptrinhmang.docx
–encrypt_data: thực hiện dowload file với nội dung đã được mã hóa. Ví dụ: download –encrypt_data laptrinhmang.docx
Chức năng chat với người dùng khác.
chat [-option] [username]: yêu cầu tạo kênh chat với user khác, yêu cầu user đó phải online.
–encrypt: nội dung chat giữa 2 user phải được mã hóa.
–multi_user [list username]: chat với nhiều người cùng một lúc.
Ví dụ: 
chat –encrypt Hans
	>>Me: Xin chao Hans, 
	>>Me: Ban co khoe khong?
	>>Hans: Chao legon.
