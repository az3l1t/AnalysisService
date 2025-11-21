package net.az3l1t.analysis.application.async.mapper;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;

import java.time.LocalDateTime;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface MessageServiceMapper {
    SendResultsDto toSendResultsDto(AnalysisResult analysisResult);

    @Mapping(target = "analysisResultId", source = "id")
    @Mapping(target = "notificationType", expression = "java(net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto.NotificationType.RESULT_UPDATED)")
    @Mapping(target = "title", expression = "java(\"Результат анализа обновлен\")")
    @Mapping(target = "message", expression = "java(\"Результат анализа №\" + analysisResult.getId() + \" был обновлен\")")
    @Mapping(target = "notificationTime", expression = "java(java.time.LocalDateTime.now())")
    @Mapping(target = "analysisTime", source = "analysisTime")
    NotificationDto toNotificationDtoForUpdate(AnalysisResult analysisResult);

    @Mapping(target = "analysisResultId", source = "id")
    @Mapping(target = "notificationType", expression = "java(net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto.NotificationType.RESULT_CONFIRMED)")
    @Mapping(target = "title", expression = "java(\"Результат анализа подтвержден\")")
    @Mapping(target = "message", expression = "java(\"Результат анализа №\" + analysisResult.getId() + \" был подтвержден врачом\")")
    @Mapping(target = "notificationTime", expression = "java(java.time.LocalDateTime.now())")
    @Mapping(target = "analysisTime", source = "analysisTime")
    NotificationDto toNotificationDtoForConfirm(AnalysisResult analysisResult);
}
