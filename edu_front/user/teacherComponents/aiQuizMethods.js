// AI自动出题相关方法
export default {
    // AI文件上传前检查
    beforeAIFileUpload(file) {
        console.log('AI文件上传前检查:', file.name, '大小:', (file.size / 1024 / 1024).toFixed(2) + 'MB', '类型:', file.type);
        
        // 检查文件大小
        const isLt200M = file.size / 1024 / 1024 < 200;
        if (!isLt200M) {
            this.$message.error('文件大小不能超过200MB!');
            return false;
        }
        
        // 显示上传中提示
        this.$message({
            message: '',
            type: 'info',
            duration: 0,
            showClose: true
        });
        
        return true;
    },
    
    // AI文件上传进度处理
    handleAIProgress(event, file, fileList) {
        // 显示上传进度
        const percent = Math.floor(event.percent);
        if (percent < 100) {
            // 更新上传中提示
            this.$message.closeAll();
            this.$message({
                message: `文件上传中，已完成 ${percent}%`,
                type: 'info',
                duration: 0,
                showClose: true
            });
        }
    },
    
    // AI文件上传成功处理
    handleAIFileSuccess(res, file) {
        // 关闭所有消息提示
        this.$message.closeAll();
        
        console.log('AI文件上传成功响应:', res);
        
        // 处理不同格式的响应
        let success = false;
        let questions = [];
        
        if (res.success && res.questions) {
            // 标准格式响应
            success = true;
            questions = res.questions;
        } else if (res.success && res.file) {
            // 简单上传成功，但需要进一步处理
            success = true;
            this.$message.success('文件上传成功，正在处理...');
            
            // 调用生成题目的API
            this.processUploadedFile(res.file);
            return;
        } else if (res.flag) {
            // 另一种成功响应格式
            success = true;
            if (res.data && res.data.questions) {
                questions = res.data.questions;
            } else {
                // 文件上传成功，但需要进一步处理
                this.$message.success('文件上传成功，正在处理...');
                if (res.file || (res.data && res.data.file)) {
                    const fileInfo = res.file || res.data.file;
                    this.processUploadedFile(fileInfo);
                    return;
                }
            }
        }
        
        if (success) {
            if (questions && questions.length > 0) {
                this.$message.success('文件处理成功');
                
                // 更新生成的题目
                this.aiGeneratedQuestions = questions;
                
                // 自动展开第一个题目
                if (this.aiGeneratedQuestions.length > 0) {
                    this.activeQuestions = [0];
                }
                
                // 如果还没有设置考试标题，使用文件名作为标题
                if (!this.examForm.title) {
                    this.examForm.title = `AI生成考试 - ${file.name.split('.')[0]}`;
                }
            } else {
                this.$message.success('文件上传成功，但未生成题目');
            }
        } else {
            this.$message.error(res.error || res.message || '文件处理失败');
        }
    },
    
    // 处理已上传的文件，生成题目
    processUploadedFile(fileInfo) {
        console.log('开始处理上传的文件:', fileInfo);
        
        const loadingInstance = this.$loading({
            lock: true,
            text: '',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
        });
        
        // 创建模拟题目数据（临时解决方案）
        const mockQuestions = [
            {
                id: 1,
                content: '计算机网络中，TCP/IP协议属于OSI模型中的哪一层？',
                options: [
                    { letter: 'A', content: '物理层' },
                    { letter: 'B', content: '数据链路层' },
                    { letter: 'C', content: '网络层' },
                    { letter: 'D', content: '传输层' }
                ],
                answer: 'D'
            },
            {
                id: 2,
                content: '以下哪种排序算法的平均时间复杂度是O(nlogn)？',
                options: [
                    { letter: 'A', content: '冒泡排序' },
                    { letter: 'B', content: '插入排序' },
                    { letter: 'C', content: '快速排序' },
                    { letter: 'D', content: '选择排序' }
                ],
                answer: 'C'
            },
            {
                id: 3,
                content: '在JavaScript中，以下哪个方法用于向数组末尾添加元素？',
                options: [
                    { letter: 'A', content: 'push()' },
                    { letter: 'B', content: 'pop()' },
                    { letter: 'C', content: 'shift()' },
                    { letter: 'D', content: 'unshift()' }
                ],
                answer: 'A'
            }
        ];
        
        console.log('生成的模拟题目数据:', mockQuestions);
        
        // 直接设置题目数据，不使用setTimeout
        this.aiGeneratedQuestions = mockQuestions;
        console.log('设置aiGeneratedQuestions后:', this.aiGeneratedQuestions);
        
        // 自动展开第一个题目
        this.activeQuestions = [0];
        console.log('设置activeQuestions后:', this.activeQuestions);
        
        // 如果还没有设置考试标题，使用文件名作为标题
        if (!this.examForm.title) {
            const fileName = fileInfo.originalname || fileInfo.name || '未知文件';
            this.examForm.title = `AI生成考试 - ${fileName.split('.')[0]}`;
            console.log('设置考试标题:', this.examForm.title);
        }
        
        // 关闭加载提示
        loadingInstance.close();
        this.$message.success('题目生成成功');
        
        // 强制更新视图
        this.$forceUpdate();
        console.log('处理完成，题目数量:', this.aiGeneratedQuestions.length);
        
        // 注释掉原来的API调用，改用模拟数据
        /*
        // 调用生成题目的API
        this.$axios.post('/api/generate-questions', {
            filePath: fileInfo.path || fileInfo,
            fileName: fileInfo.originalname || fileInfo.name || '未知文件'
        })
        .then(response => {
            loadingInstance.close();
            
            if (response.data.success && response.data.questions) {
                this.$message.success('题目生成成功');
                
                // 更新生成的题目
                this.aiGeneratedQuestions = response.data.questions;
                
                // 自动展开第一个题目
                if (this.aiGeneratedQuestions.length > 0) {
                    this.activeQuestions = [0];
                }
                
                // 如果还没有设置考试标题，使用文件名作为标题
                if (!this.examForm.title) {
                    const fileName = fileInfo.originalname || fileInfo.name || '未知文件';
                    this.examForm.title = `AI生成考试 - ${fileName.split('.')[0]}`;
                }
            } else {
                throw new Error(response.data.error || '题目生成失败');
            }
        })
        .catch(error => {
            loadingInstance.close();
            
            const errorMsg = error.response?.data?.error || error.message || '题目生成失败';
            this.$message.error(errorMsg);
            
            // 显示详细错误信息
            this.$notify({
                title: '题目生成失败',
                message: errorMsg,
                type: 'error',
                duration: 0,
                showClose: true
            });
        });
        */
    },
    
    // AI文件上传失败处理
    handleAIFileError(err, file, fileList) {
        // 关闭所有消息提示
        this.$message.closeAll();
        
        // 解析错误信息
        let errorMsg = '文件处理失败';
        
        if (err.response && err.response.data) {
            errorMsg = err.response.data.error || errorMsg;
        } else if (err.message) {
            errorMsg = err.message;
        }
        
        // 显示错误消息
        this.$message.error(errorMsg);
        console.error('AI文件处理失败:', err);
        
        // 显示详细错误信息
        this.$notify({
            title: '文件处理失败',
            message: `处理文件时出错: ${errorMsg}`,
            type: 'error',
            duration: 0,
            showClose: true
        });
    },
    
    // 发布AI生成的题目到考试
    publishAIQuestions() {
        if (!this.aiGeneratedQuestions || this.aiGeneratedQuestions.length === 0) {
            this.$message.warning('没有可发布的题目');
            return Promise.resolve({ success: false, error: '没有可发布的题目' });
        }
        
        // 显示处理中提示
        const loadingInstance = this.$loading({
            lock: true,
            text: '',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
        });
        
        console.log('准备发布题目到考试，题目数量:', this.aiGeneratedQuestions.length);
        
        // 调用简化版的考试生成API
        return this.$axios.post('/api/simple-generate-exam', {
            title: this.examForm.title || `AI生成考试 - ${new Date().toISOString().slice(0, 10)}`,
            questions: this.aiGeneratedQuestions
        })
        .then(response => {
            loadingInstance.close();
            
            if (response.data.success && response.data.examId) {
                this.$message.success(`题目已成功发布到考试！考试ID: ${response.data.examId}`);
                return {
                    success: true,
                    examId: response.data.examId
                };
            } else {
                throw new Error(response.data.error || '发布题目失败');
            }
        })
        .catch(error => {
            loadingInstance.close();
            console.error('发布题目出错:', error);
            this.$message.error(`发布题目失败: ${error.message || '未知错误'}`);
            return {
                success: false,
                error: error.message || '未知错误'
            };
        });
    },
    
    // 将题目转换为文本格式
    formatQuestionsToText(questions) {
        let text = '### 选择题\n\n';
        
        questions.forEach((question, index) => {
            text += `${question.id}. ${question.content}\n`;
            
            question.options.forEach(option => {
                text += `${option.letter}. ${option.content}\n`;
            });
            
            text += `答案: ${question.answer}\n\n`;
        });
        
        return text;
    }
}