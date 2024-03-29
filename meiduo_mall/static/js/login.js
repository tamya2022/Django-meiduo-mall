var vm = new Vue({
    el: '#app',
	// 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        error_username: false,
        error_password: false,
		error_username_message: '请输入5-20个字符的用户名',
		error_password_message: '请输入8-12位的密码',
        username: '',
        password: '',
        remembered: true
    },
    methods: {
        // 检查账号
        check_username: function(){
        	var re = /^[a-zA-Z0-9_-]{5,20}$/;
			if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username = true;
            }
        },
		// 检查密码
        check_pwd: function(){
        	var re = /^[0-9A-Za-z]{8,20}$/;
			if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 表单提交
        on_submit: function(){
            this.check_username();
            this.check_pwd();
            if (this.error_username === true || this.error_pwd === true) {
                // 不满足登录条件：禁用表单
				window.event.returnValue = false
                // return false;
            }
        },
    }
});
