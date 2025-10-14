package net.az3l1t.analysis.application.async.mapper;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface MessageServiceMapper {
    SendResultsDto toSendResultsDto(AnalysisResult analysisResult);
}
