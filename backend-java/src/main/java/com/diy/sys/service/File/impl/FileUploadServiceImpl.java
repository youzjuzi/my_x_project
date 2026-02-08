package com.diy.sys.service.File.impl;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.diy.config.CloudflareR2Config;
import com.diy.sys.service.File.IFileUploadService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

/**
 * 文件上传服务实现类
 */
@Slf4j
@Service
public class FileUploadServiceImpl implements IFileUploadService {

    @Autowired
    private AmazonS3 amazonS3;

    @Autowired
    private CloudflareR2Config r2Config;

    @Override
    public String uploadFile(MultipartFile file, String folder) {
        if (file == null || file.isEmpty()) {
            throw new RuntimeException("文件不能为空");
        }

        // 验证文件类型
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null) {
            throw new RuntimeException("文件名不能为空");
        }

        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new RuntimeException("只能上传图片文件");
        }

        // 验证文件大小（5MB）
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new RuntimeException("文件大小不能超过 5MB");
        }

        try {
            // 生成唯一文件名
            String fileExtension = getFileExtension(originalFilename);
            String fileName = folder + UUID.randomUUID().toString() + "." + fileExtension;

            // 上传到 R2
            InputStream inputStream = file.getInputStream();
            ObjectMetadata metadata = new ObjectMetadata();
            metadata.setContentLength(file.getSize());
            metadata.setContentType(contentType);

            PutObjectRequest putObjectRequest = new PutObjectRequest(
                    r2Config.getBucketName(),
                    fileName,
                    inputStream,
                    metadata
            );

            amazonS3.putObject(putObjectRequest);

            // 返回文件访问URL
            if (StringUtils.hasText(r2Config.getDomain())) {
                // 如果配置了自定义域名，使用自定义域名
                return r2Config.getDomain() + "/" + fileName;
            } else {
                // 否则使用 R2 的公共 URL（需要先配置公共访问）
                return amazonS3.getUrl(r2Config.getBucketName(), fileName).toString();
            }

        } catch (IOException e) {
            log.error("文件上传失败", e);
            throw new RuntimeException("文件上传失败: " + e.getMessage());
        }
    }

    @Override
    public boolean deleteFile(String fileUrl) {
        if (!StringUtils.hasText(fileUrl)) {
            return false;
        }

        try {
            // 从 URL 中提取文件路径
            String fileName = extractFileNameFromUrl(fileUrl);
            if (fileName == null) {
                return false;
            }

            amazonS3.deleteObject(r2Config.getBucketName(), fileName);
            return true;
        } catch (Exception e) {
            log.error("删除文件失败: {}", fileUrl, e);
            return false;
        }
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex > 0 && lastDotIndex < filename.length() - 1) {
            return filename.substring(lastDotIndex + 1).toLowerCase();
        }
        return "jpg"; // 默认扩展名
    }

    /**
     * 从 URL 中提取文件名
     */
    private String extractFileNameFromUrl(String fileUrl) {
        if (!StringUtils.hasText(fileUrl)) {
            return null;
        }

        // 如果使用自定义域名
        if (r2Config.getDomain() != null && fileUrl.startsWith(r2Config.getDomain())) {
            return fileUrl.substring(r2Config.getDomain().length() + 1);
        }

        // 从完整 URL 中提取路径
        int lastSlashIndex = fileUrl.lastIndexOf('/');
        if (lastSlashIndex >= 0 && lastSlashIndex < fileUrl.length() - 1) {
            return fileUrl.substring(lastSlashIndex + 1);
        }

        return null;
    }
}

