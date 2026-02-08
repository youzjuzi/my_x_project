package com.diy.sys.service.File;

import org.springframework.web.multipart.MultipartFile;

/**
 * 文件上传服务接口
 */
public interface IFileUploadService {
    
    /**
     * 上传文件到 Cloudflare R2
     * @param file 文件
     * @param folder 文件夹路径（如：avatar/）
     * @return 文件访问URL
     */
    String uploadFile(MultipartFile file, String folder);
    
    /**
     * 删除文件
     * @param fileUrl 文件URL
     * @return 是否删除成功
     */
    boolean deleteFile(String fileUrl);
}

