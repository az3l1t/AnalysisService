package net.az3l1t.analysis.infrastructure.adapter.in.rest.mapper;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.GetOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.UpdateOutResultDto;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface ResultControllerMapper {
    UpdateOutResultDto toDtoUpdate(AnalysisResult analysisResult);
    GetOutResultDto toDtoGet(AnalysisResult analysisResult);
}
